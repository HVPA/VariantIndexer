import sys, os
from suds.client import Client
import base64
from django.core.management import setup_environ

# path where Portal django app is located, this usually 1 directory up from 
# where the app sits. e.g: '/path/location/Portal' then put down '/path/location'
path = ''
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'Portal.settings'

from Portal import settings
setup_environ(settings)

from Portal.hvp.models.search.Gene import Gene
from Portal.hvp.models.search.Variant import Variant
from Portal.search.hgvs_parser.Parser import Parser

# get all variants
variant_list = Variant.objects.all()
parser = Parser()

for variant in variant_list:
    if variant.cDNA != 'None':
        try:
	        v = parser.parse('', variant.cDNA)
        	
            if v.position:
                variant.Position = v.position.replace('*','')
                if v.position_intron:
                    variant.PositionIntron = v.position_intron.replace('*','')
            else:
                if v.range_lower:
                    variant.LowerRange = v.range_lower.replace('*','')
                
                    if v.range_lower_intron:
                        variant.LowerRangeIntron = v.range_lower_intron.replace('*','')
                    
                    variant.UpperRange = v.range_upper.replace('*','')
                
                    if v.range_upper_intron:
                        variant.UpperRangeIntron = v.range_upper_intron.replace('*','')
        
            variant.Operator = v.operator
            variant.OperatorValue = v.operator_value
        
            variant.save()
        except:
            print 'Could not index variant: ' + variant.cDNA
        

