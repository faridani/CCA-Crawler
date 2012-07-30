from scrapy.conf import settings
from scrapy.contrib.exporter import CsvItemExporter

class ZapposExporter (CsvItemExporter):

    def __init__ (self, *args, **kwargs):
        kwargs['fields_to_export'] = settings.getlist('EXPORT_FIELDS') or None
        kwargs['encoding'] = settings.get('EXPORT_ENCODING', 'utf-8')
        super(ZapposExporter, self).__init__(*args, **kwargs)