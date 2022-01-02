from cloud_console_common.models import *
from cloud_console_common.plugin import *
from cloud_console_common import log
import boto3


class Boto3Ec2Client(Auth):

    def authenticate(self, **kwargs):
        # This implementation only support standard environmental credentials for boto3 at this stage
        self.authenticated = True
        self.authenticated_client = boto3.client('ec2')
        return self.authenticated_client


class InstanceStateExtractLogic(ExtractLogic):

    def extract(self, raw_data)->dict:
        """
            Expecting a dict with the Instance data - # Reservations[].Instances[].raw_data with the following in raw_data:

            'State': {
                'Code': 80,
                'Name': 'stopped'
            }, 
        """
        state = dict()
        state['Code'] = None
        state['Name'] = 'Unknown'
        if 'State' in raw_data:
            state = copy.deepcopy(raw_data['State'])
            if 'Name' in state:
                state['Name'] = state['Name'].title()
        return state


class InstanceNameExtractLogic(ExtractLogic):

    def extract(self, raw_data)->dict:
        """
            Expecting a dict with the Instance data - # Reservations[].Instances[].raw_data with the following in raw_data:

            'Tags': [
                {
                    'Key': 'Name', 
                    'Value': 'machine-01'
                }
            ], 
        """
        name_data = dict()
        name_value = '-'
        for tag_data in raw_data['Tags']:
            if tag_data['Key'] == 'Name':
                name_value = tag_data['Value']
        name_data['Name'] = name_value
        return name_data


class InstancesExtractLogic(ExtractLogic):

    def extract(self, raw_data)->dict:
        # Expecting the raw response from the AWS EC2 API call "describe-instances"  - Reservations[].Instances[].raw_data
        instances = dict()
        for reservation in raw_data['Reservations']:
            for instance in reservation['Instances']:
                instances[instance['InstanceId']] = copy.deepcopy(instance)
        return instances


class SingleInstanceExtractLogic(ExtractLogic):
    def extract(self, raw_data)->dict:
        return copy.deepcopy(raw_data)


class Ec2DescribeInstancesRemoteCallLogic(RemoteCallLogic):

    def execute(self, authenticated_client: object=None)->dict:
        response = authenticated_client.describe_instances()
        instances = self.extract_logic.extract(raw_data=response) 
        self.base_data = copy.deepcopy(instances)
        return instances


class Ec2MetaDataRemoteCallLogic(RemoteCallLogic):

    def execute(self, authenticated_client: object=None)->dict:
        instance_meta_data = self.extract_logic.extract(raw_data=copy.deepcopy(self.base_data))
        return instance_meta_data



class InstancesDataPoint(DataPoint):

    def get_ui_display_value(self)->str:
        return self.label


class SingleInstanceDataPoint(DataPoint):

    def get_ui_display_value(self)->str:
        return self.name


class InstanceStateDataPoint(DataPoint):

    def get_ui_display_value(self)->str:
        return '[{}] {}'.format(
            self.value['Code'],
            self.value['Name']
        )

class InstanceNameDataPoint(DataPoint):

    def get_ui_display_value(self)->str:
        return '{}'.format(self.value['Name'])


instances_data_point = InstancesDataPoint(
    name='ec2_instances', 
    label='EC2 Instances', 
    initial_value=dict(), 
    remote_call_logic=Ec2DescribeInstancesRemoteCallLogic(extract_logic=InstancesExtractLogic()),
    ui_section_name='services',
    ui_tab_name='Compute',
    ui_identifier='instances'
)


class Instances(Service):

    def __init__(
        self,
        service_name='aws_ec2_instances',
        ui_label='AWS EC2 Instances',
        data_point=instances_data_point,
        max_cache_lifetime=300,
        service_config=dict()
    ):
        super().__init__(
            service_name=service_name,
            ui_label=ui_label,
            data_point=data_point,
            max_cache_lifetime=max_cache_lifetime,
            service_config=service_config
        )

    def service_init(self, authenticated_client: object=None):
        self.data_object_cache.data_point.children_data_points = dict()
        self.data_object_cache.refresh_cache(force=True, authenticated_client=authenticated_client)



