from haystack import indexes
from dfchatbox.models import Procedure

class ProcedureIndexENG(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	nameSLO = indexes.CharField(model_attr='nameSLO')
	procedure_id = indexes.CharField(model_attr='procedure_id')

	def get_model(self):
		return Procedure

