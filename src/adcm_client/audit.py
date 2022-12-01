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

from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from adcm_client.base import RichlyTypedAPIList, RichlyTypedAPIObject

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
    FAIL = 'fail'
    DENIED = 'denied'


class AuditOperation(RichlyTypedAPIObject):
    """
    Audit operation object with info about operation/action result.

    Using enums and datetime as field types is experimental.
    If type conversion fails, type may "degrade" to a string.
    """

    IDNAME = 'id'
    PATH = ['audit', 'operation']
    FILTERS = [
        'object_type',
        'object_name',
        'operation_type',
        'operation_name',
        'operation_result',
        'operation_date',
        'username',
    ]

    id: Optional[int] = None

    object_id: Optional[int] = None
    object_type: Optional[ObjectType] = None
    object_name: Optional[str] = None
    # keys are: current, previous
    object_changes: Optional[Dict[str, dict]] = None

    operation_type: Optional[OperationType] = None
    operation_name: Optional[str] = None
    operation_result: Optional[OperationResult] = None
    operation_time: Optional[datetime] = None

    user_id: int = None

    def _convert(self):
        self._convert_enum('object_type', ObjectType)
        self._convert_enum('operation_type', OperationType)
        self._convert_enum('operation_result', OperationResult)
        self._convert_datetime('operation_time')


class AuditOperationList(RichlyTypedAPIList):
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


class AuditLogin(RichlyTypedAPIObject):
    """Audit record with login result"""

    IDNAME = 'id'
    PATH = ['audit', 'login']
    FILTERS = ['login_result', 'login_date', 'username']
    API_ONLY_FILTERS = ("username",)

    id: Optional[int] = None
    user_id: Optional[int] = None
    login_result: Optional[LoginResult] = None
    login_time: Optional[datetime] = None
    login_details: Optional[dict] = None

    def _convert(self):
        self._convert_enum('login_result', LoginResult)
        self._convert_datetime('login_time')


class AuditLoginList(RichlyTypedAPIList):
    """List of `AuditLogin` objects"""

    _ENTRY_CLASS = AuditLogin
