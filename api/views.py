import time

from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

import redis

from .serializers import VisitedLinksSerializer


redis_cli = redis.Redis(settings.REDIS_HOST, settings.REDIS_PORT, charset="utf-8", decode_responses=True)


class VisitedLinksView(generics.GenericAPIView):
    serializer_class = VisitedLinksSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as er:
            return Response(data={'status': er.args}, status=status.HTTP_400_BAD_REQUEST)

        unique_domains = ":::".join(serializer.data["links"])

        curr_time = time.time()

        redis_cli.zadd('domains', {unique_domains: curr_time})

        return Response(data={'status': 'ok'})


class VisitedDomainsView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):

        result_validate_query_params = self.validate_query_params()

        if not result_validate_query_params[0]:
            return Response(data={'status': result_validate_query_params[1]}, status=status.HTTP_400_BAD_REQUEST)

        domains_result = redis_cli.zrangebyscore('domains', result_validate_query_params[1]['from'],
                                                 result_validate_query_params[1]['to'])

        unique_domains = set()

        for domains in domains_result:
            ds = domains.split(':::')
            for d in ds:
                unique_domains.add(d)

        return Response(data={"domains": list(unique_domains), 'status': 'ok'})

    def validate_query_params(self):
        if (not self.request.query_params.get("from")) or (not self.request.query_params.get("to")):
            return False, 'request must contain get parameters - "from" and "to" '

        try:
            float(self.request.query_params.get("from"))
            float(self.request.query_params.get("to"))
        except ValueError:
            return False, 'get parameters - "from" and "to" must contain only float numbers'

        if float(self.request.query_params.get("from")) < 0 or float(self.request.query_params.get("to")) < 0:
            return False, 'get parameters - "from" and "to" must be greater than zero'

        if float(self.request.query_params.get("from")) > float(self.request.query_params.get("to")):
            return False, 'get parameter - "from" must be less or equal to "to"'

        return True, {'from': float(self.request.query_params.get("from")),
                      'to': float(self.request.query_params.get("to"))}
