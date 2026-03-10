from flexget import plugin
from flexget.event import event
import re

class IMDBTagPlugin:
    schema = {'type': 'boolean'}

    def on_task_modify(self, task, config):
        if not config:
            return
        for entry in task.entries:
            description = entry.get('description')
            if description:
                match = re.search(r'(tt\d{7,8})', description)
                if match:
                    entry['tags'] = [match.group(1)]
                    
@event('plugin.register')
def register_plugin():
    plugin.register(IMDBTagPlugin, 'imdb_tag', api_ver=2)
