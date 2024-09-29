# from rest_framework import generics
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAdminUser, IsAuthenticated
# from rest_framework.request import HttpRequest
# from rest_framework.response import Response
# from rest_framework.views import APIView


# @permission_classes((IsAuthenticated))
# @api_view(http_method_names=["GET"])
# def get_data_for_chart(request: HttpRequest, challenge_pk: int):
#     if request.method == "GET":
#         return Response({})
