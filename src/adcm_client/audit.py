# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Audit-related objects"""

import datetime
from enum import Enum
from typing import Dict, Optional

from adcm_client.base import BaseAPIObject, BaseAPIListObject, RichlyTypedObject


##################################################
#              O P E R A T I O N
##################################################


class ObjectType(Enum):
    """Possible object type options for audit operation"""

    ADCM = 'adcm'
    BUNDLE = 'bundle'
    CLUSTER = 'cluster'
    SERVICE = 'service'
    COMPONENT = 'component'
    PROVIDER = 'provider'
    HOST = 'host'

    ROLE = 'role'
    POLICY = 'policy'
    USER = 'user'
    GROUP = 'group'


class OperationType(Enum):
    """Audit Operations type"""

    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'


class OperationResult(Enum):
    """Result of audited operation"""

    SUCCESS = 'success'
    FAILURE = 'fail'
    DENIED = 'denied'


class AuditOperation(BaseAPIObject, RichlyTypedObject):
    """
    Audit operation object with info about operation/action result.

    Using enums and datetime as field types is experimental.
    If type conversion fails, type may "degrade" to a string.
    """

    PATH = ['audit', 'operation']
    FILTERS = [
        'object_type',
        'object_name',
        'operation_type',
        'operation_name',
        'operation_result',
        'operation_time',
        'username',
    ]

    id: int = None

    object_id: int = None
    object_type: ObjectType = None
    object_name: str = None
    # keys are: current, previous
    object_changes: Optional[Dict[str, dict]] = None

    operation_type: OperationType = None
    operation_name: str = None
    operation_result: OperationResult = None
    operation_time: datetime.datetime = None

    user_id: int = None

    def _convert(self):
        self._convert_enum('object_type', ObjectType)
        self._convert_enum('operation_type', OperationType)
        self._convert_enum('operation_result', OperationResult)
        self.operation_time = datetime.datetime.fromisoformat(self.operation_time)


class AuditOperationList(BaseAPIListObject):
    """List of `AuditOperation` objects"""

    _ENTRY_CLASS = AuditOperation


##################################################
#              L O G I N
##################################################


class LoginResult(Enum):
    """Audit login results"""

    SUCCESS = 'success'
    USER_NOT_FOUND = 'user not found'
    WRONG_PASSWORD = 'wrong password'
    DISABLED = 'account disabled'


class AuditLogin(BaseAPIObject, RichlyTypedObject):
    """Audit record with login result"""

    PATH = ['audit', 'login-session']

    id: int = None
    user_id: int = None
    login_result: LoginResult = None
    login_time: datetime.datetime = None

    def _convert(self):
        self._convert_enum('login_result', LoginResult)
        self.login_time = datetime.datetime.fromisoformat(self.login_time)


class AuditLoginList(BaseAPIListObject):
    """List of `AuditLogin` objects"""

    _ENTRY_CLASS = AuditLogin
