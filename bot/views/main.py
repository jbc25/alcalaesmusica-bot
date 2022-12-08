
import json
from django.http import JsonResponse
from django.views import View
from telegram import Update


class AemBotView(View):

    def post(self, request, *args, **kwargs):

        from ..apps import dispatcher, bot

        body = json.loads(request.body)
        dispatcher.process_update(Update.de_json(body, bot))
        return JsonResponse({"ok": "POST request processed"})

