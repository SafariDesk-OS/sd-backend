from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status # Import status

from tenant.models import SLA, SLATarget, SLACondition, SLAReminder, SLAEscalations, Department, BusinessHoursx, \
    Holidays, SLAEscalation, SLAConfiguration
from tenant.serializers.SlaXSerializer import SLASerializer, BusinessHoursSerializer, HolidaySerializer, SLAConfigurationSerializer
from users.models import Users


class SLAConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing SLA configuration settings"""
    queryset = SLAConfiguration.objects.all()
    serializer_class = SLAConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SLAConfiguration.objects.all()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current SLA configuration (create if doesn't exist)"""
        config, created = SLAConfiguration.objects.get_or_create(
            pk=1,
            defaults={'allow_sla': True, 'allow_holidays': True}
        )
        serializer = self.get_serializer(config)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_config(self, request):
        """Update the current SLA configuration"""
        config, created = SLAConfiguration.objects.get_or_create(pk=1)
        serializer = self.get_serializer(config, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'SLA configuration updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holidays.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Holidays.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class BusinessHoursViewSet(viewsets.ModelViewSet):
    """ViewSet for managing business hours"""
    queryset = BusinessHoursx.objects.all()
    serializer_class = BusinessHoursSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BusinessHoursx.objects.all().order_by('day_of_week')
    
    def create(self, request, *args, **kwargs):
        """Create business hours - supports both single and bulk creation"""
        # Handle wrapped data format {data: [...]}
        data = request.data.get('data', request.data)
        
        # Support both single object and array
        many = isinstance(data, list)
        
        # Transform weekday to day_of_week if present
        if many:
            for item in data:
                if 'weekday' in item and 'day_of_week' not in item:
                    item['day_of_week'] = item.pop('weekday')
        else:
            if 'weekday' in data and 'day_of_week' not in data:
                data['day_of_week'] = data.pop('weekday')
        
        serializer = self.get_serializer(data=data, many=many)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Business hours created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update business hours"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Business hours updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete business hours"""
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Business hours deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class SLAViewSet(viewsets.ModelViewSet):
    queryset = SLA.objects.all()
    serializer_class = SLASerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = SLA.objects.prefetch_related(
            'conditions',
            'targets__reminders__notify_groups',
            'targets__reminders__notify_agents',
            'targets__escalations__escalate_to_groups',
            'targets__escalations__escalate_to_agents'
        )

        # Filter by active status if requested
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.all()

    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Get all choice options for dropdowns"""
        return Response({
            'operational_hours': SLA.OPERATIONAL_HOURS_CHOICES,
            'evaluation_methods': SLA.EVALUATION_CHOICES,
            'priorities': SLATarget.PRIORITY_CHOICES,
            'time_units': SLATarget.TIME_UNITS,
            'condition_types': SLACondition.CONDITION_TYPES,
            'operators': SLACondition.OPERATORS,
            'reminder_types': SLAReminder.REMINDER_TYPES,
            'escalation_types': SLAEscalation.ESCALATION_TYPES,
        })
    @action(detail=False, methods=['get'])
    def users_and_groups(self, request):
        """Get available users and groups for assignment"""
        agents = Users.objects.filter(is_active=True, role__name='agent').values('id', 'username', 'first_name', 'last_name', 'email')
        departments = Department.objects.all().values('id', 'name')

        return Response({
            'agents': list(agents),
            'groups': list(departments)
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an SLA"""
        sla = self.get_object()
        sla.is_active = True
        sla.save()
        return Response({'status': 'SLA activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an SLA"""
        sla = self.get_object()
        sla.is_active = False
        sla.save()
        return Response({'status': 'SLA deactivated'})

    @action(detail=False, methods=['get'])
    def business_hours(self, request):
        """
        Get all business hours configurations for the authenticated user's business.
        """
        try:
            business_hours_queryset = BusinessHoursx.objects.all()
            serializer = BusinessHoursSerializer(business_hours_queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": "Error retrieving business hours",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def update_name(self, request, pk=None):
        """Update only the name of an SLA policy"""
        sla = self.get_object()
        new_name = request.data.get('name')
        
        if not new_name:
            return Response({
                'success': False,
                'message': 'Name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sla.name = new_name
        sla.save()
        
        return Response({
            'success': True,
            'message': 'SLA name updated successfully',
            'data': {'id': sla.id, 'name': sla.name}
        })

    @action(detail=True, methods=['patch'])
    def update_target(self, request, pk=None):
        """Update a specific SLA target's resolution time"""
        try:
            target_id = request.data.get('target_id')
            resolution_time = request.data.get('resolution_time')
            resolution_unit = request.data.get('resolution_unit')
            
            if not target_id:
                return Response({
                    'success': False,
                    'message': 'Target ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            target = SLATarget.objects.get(id=target_id, sla_id=pk)
            
            if resolution_time is not None:
                target.resolution_time = resolution_time
            if resolution_unit:
                target.resolution_unit = resolution_unit
            
            target.save()
            
            return Response({
                'success': True,
                'message': 'Target updated successfully',
                'data': {
                    'id': target.id,
                    'resolution_time': target.resolution_time,
                    'resolution_unit': target.resolution_unit
                }
            })
        except SLATarget.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Target not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
