from django.test import TestCase

# Create your tests here.

# from django_vue_cmdb.expiring_token_authentication import ExpireTokenAuthentication
# from rest_framework import permissions
# from rest_framework.views import APIView
# from django.http import JsonResponse
# from django.db import IntegrityError
# from django.db import transaction
# from django.db.models import Q
# from workflows.models import Workflow
# from workflows.models import DevelopVersionWorkflow
# from workflows.models import WorkflowStateEvent
# from workflows.utils import init_workflow
# from workflows.utils import check_approve_perm
# from workflows.utils import do_transition
# from workflows.utils import relate_approve_user_to_wse
# from workflows.utils import get_workflow_chain
# from workflows.utils import get_workflow_chain_with_wse
# from workflows.utils import get_approve_pending_cnt
# class WorkflowSubmit(APIView):
#     """    工单提交    :param: {
#             'workflow_id': 1,          # 流程id
#                     'apply_form_data': {       # 申请表单内容            ...        },
#                        }    """
#     authentication_classes = (ExpireTokenAuthentication,)
#     permission_classes = (permissions.IsAuthenticated,)
#     def post(self, request, version):
#         result = {
#             'code': 0,
#             'msg': '请求成功',
#             'data': {}
#         }
#         try:
#             with transaction.atomic():
#         # 校验操作权限
#         if not check_user_sso_perm(request.user, 'workflows.workflow_submit'):
#             raise PermissionError
#             pass
#             raw_data = request.data
#             workflow_abbr = raw_data.get('workflow_abbr', '')
#             workflow = Workflow.objects.get(abbr=workflow_abbr)
#             workflow_abbr = workflow.abbr
#             # 发版申请
#             if workflow_abbr == 'develop_version':
#                 title = raw_data.get('title')
#                 test_content = raw_data.get('test_content', '')
#                 dev_content = raw_data.get('dev_content', '')
#                 # 保存申请单内容
#                 obj = DevelopVersionWorkflow.objects.create(
#                     title=title,
#                     creator=request.user,
#                     workflow=workflow,
#                     test_content=test_content,
#                     dev_content=dev_content
#                 )
#                 # 创建流程事件
#                 wse = WorkflowStateEvent.objects.create(
#                     content_object=obj, create_time=obj.create_time, creator=request.user, title=obj.title,                        state=workflow.init_state, is_current=True)
#                 # 初始化工单流
#                 init_workflow(workflow, obj, wse)
#                 except PermissionError:
#                     result = {                'code': 403,                'msg': '权限受限',                'data': {}            }
#                 except Workflow.DoesNotExist as e:
#                     result = {                'code': 403,                'msg': str(e),                'data': {}            }
#                 except IntegrityError:\
#                     result = {                'code': 200,                'msg': '记录重复',                'data': {}            }
#                 except Exception as e:
#                     result = {                'code': 500,                'msg': str(e),                'data': {}            }
#                 finally:
#                     return JsonResponse(result)
#
#
# class WorkflowApprove(APIView):
#     """    工单审批    :param: {        'wse_id': 2,                # 必选，审批的流程事件id        'select': '同意',           # 必选，审批选项        'opinion': '意见',          # 非必选，审批文字意见        'approve_form_data': {      # 非必选，审批表单内容            ...        }    }    """
#     authentication_classes = (ExpireTokenAuthentication,)
#     permission_classes = (permissions.IsAuthenticated,)
#     def post(self, request, version):
#         result = {            'code': 0,            'msg': '请求成功',            'data': {}        }
#         try:
#             with transaction.atomic():
#                 approve_user = request.user
#                 raw_data = request.data
#                 wse_id = raw_data.get('wse_id')
#                 wse = WorkflowStateEvent.objects.get(pk=wse_id)
#                 dev_content = raw_data.get('dev_content', '')
#                 code_merge = raw_data.get('code_merge', '')
#                 # 如果有研发人员填写内容，则需要保存
#                 if dev_content:
#                     wse.content_object.dev_content = dev_content
#                     if code_merge:
#                         wse.content_object.code_merge = code_merge
#                         wse.content_object.save(update_fields=['dev_content', 'code_merge'])
#                         # 审批权限检验
#                         success, msg = check_approve_perm(wse, approve_user)
#                         if not success:
#                             raise Exception(msg)
#                             # 流程流转
#                             select = raw_data.get('select')
#                             opinion = raw_data.get('opinion', None)
#                             success, msg, new_wse = do_transition(wse, select, opinion, approve_user)
#                             if success:
#                             # 关联新审批人
#                                 relate_approve_user_to_wse(new_wse.state, new_wse.content_object, new_wse)
#                                 if new_wse.users.all():
#                                 # 发送钉钉通知给下一批审批人员
#                                     pass
#                                 else:
#                                 # 工单审批完成，继续下一步操作
#                                     pass
#                             else:
#                                 raise Exception(msg)
#                                 except WorkflowStateEvent.DoesNotExist as e:
#                                     result = {                'code': 500,                'msg': str(e),                'data': {}            }
#                                 except PermissionError:
#                                     result = {                'code': 403,                'msg': '权限受限',                'data': {}            }
#                                 except IntegrityError:
#                                     result = {                'code': 200,                'msg': '记录重复',                'data': {}            }
#                                 except Exception as e:
#                                     result = {                'code': 500,                'msg': str(e),                'data': {}            }
#                                 finally:
#                                     return JsonResponse(result)