import sys, os, base64, time, suds, re
from suds.client import Client
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
from Portal.hvp.models.search.HG_Build import HG_Build
from Portal.search.hgvs_parser.Validator import Validator
from Portal.search.hgvs_parser.Parser import Parser

# mutalyzer soap url
URL = 'https://mutalyzer.nl/services/?wsdl'

# get genomic build number
hg_build = HG_Build.objects.all()[0].BuildNumber

# get all variants
variant_list = Variant.objects.all()

# extract all the variants cDNA, refseq, refseqver and output to txt file
v = Validator()
file = open('input.txt', 'w')
for variant in variant_list:
    if v.validate(variant.cDNA):
        file.write(variant.Gene.RefSeqName + '.' + variant.Gene.RefSeqVer + ':' + variant.cDNA + '\n')
    
file.close()

# encode file to base64 binary
encoded = open('input.txt', 'rb').read().encode("base64")

print 'Connecting to web services...'

c = Client(URL, cache=None)
o = c.service

print 'Submitting Batch Job...'

batchJobID = o.submitBatchJob(encoded, 'PositionConverter', hg_build)

print 'Batch job submitted'
print 'BatcheJobID: ' + str(batchJobID)

print "Retrieving results... "
resultFinished = False
while not resultFinished:
    try:
        time.sleep(5) # wait 5 secs
        encodedResults = o.getBatchJob(batchJobID)
        resultFinished = True
    except suds.WebFault as e:
        resultFinished = False
    except:
        resultFinished = False

# decode results
decoded = base64.b64decode(encodedResults)

#write results to file for referencing/debugging
file = open('result.txt', 'w')
file.write(decoded)
file.close()

# write genomic results back into database hvp_variant table
results_list = decoded.splitlines()
parser = Parser()
# extract the data from results
for result in results_list:
    # skip the header on the first line
    if 'Input Variant' not in result:
        # split the line up by 'tabs'
        line = re.split(r'\t+', result)
        
        # original values submitted
        cDNA_value = line[0].split(':')
        
        cDNA_ref = cDNA_value[0]
        cDNA_ref_split = cDNA_ref.split('.')
        cDNA_refName = cDNA_ref_split[0]
        cDNA_refVer = cDNA_ref_split[1]
        cDNA_var = cDNA_value[1]
        
        # genomic values should 2nd item(tab)
        genomic_value = line[1].split(':')
        
        genomic_ref = genomic_value[0]
        error = False
        
        try:
            genomic_ref_split = genomic_ref.split('.')
            genomic_refName = genomic_ref_split[0]
            genomic_refVer = genomic_ref_split[1]
            genomic_var = genomic_value[1]
            gp = parser.parse('', genomic_var)
            if gp.position != '':
                genomic_position = gp.position
            else:
                genomic_position = gp.range_lower
        except:
            error = True
            genomic_ref_split = ''
            genomic_refName = line[1]
            genomic_refVer = ''
            genomic_var = ''
            genomic_position = ''
            # print errors
            print 'Error: Could not convert ' + cDNA_refName + '.' + cDNA_refVer + ' ' + cDNA_var  + ' | ' + genomic_refName + '.' + genomic_refVer + ' ' + genomic_var + ' ' + genomic_position
        
        # save results to hvp db
        if not error:
            variant_list = Variant.objects.filter(cDNA = cDNA_value[1], Gene__RefSeqName = cDNA_refName, Gene__RefSeqVer = cDNA_refVer)
            if len(variant_list) >= 1:
                # if there are multiple variants then save the genomic ref for each one
                for variant in variant_list:
                    variant.CalculatedGenomic = genomic_var
                    variant.GenomicPosition = genomic_position
                    variant.GenomicRefSeq = genomic_refName
                    variant.GenomicRefSeqVer = genomic_refVer
                
                    # save
                    variant.save()
    
    
