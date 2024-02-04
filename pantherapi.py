
import pdb
import requests
import time
import json
import click

class PantherAPI(object):
    """
    A class for accessing the PANTHER API.
    """
    def __init__(self):
        self.baseurl = "https://pantherdb.org"

    ### note that human is 9606 and mouse is 10090   
    def get_enrichment(self,
                       gene_input_list,
                       organism,
                       annotation_data_set,
                       ref_input_list = None,
                       ref_organism = None,
                       enrichment_test_type='FISHER',
                       correction='FDR',
                       ):
        """
        Returns a dictionary of enrichment results from the PANTHER API.
        """

        if ref_input_list is not None or ref_organism is not None:
            raise Exception("Error: Reference input list and reference organism are not implemented yet.")

        suburl = "/services/oai/pantherdb/enrich/overrep"
        url = self.baseurl + suburl

        headers = {"accept": "application/json"}
        data = {
            "geneInputList": gene_input_list,
            "organism": organism,
            "annotDataSet": annotation_data_set,
            "enrichmentTestType": enrichment_test_type,
            "correction": correction
        }
        response = requests.post(url, headers=headers, data=data)
        if response.ok:
            return response.json()
    
    def get_supportedannotdatasets(self):
        suburl = "/services/oai/pantherdb/supportedannotdatasets"
        url = self.baseurl + suburl
        response = requests.get(url)
        if response.ok:
            response_dat = response.json()
            return response_dat["search"]['annotation_data_sets']['annotation_data_type']
        else:
            raise Exception("Error: {}".format(response.status_code))

    def get_list_of_available_genomes(self):
        """
        Returns a list of available genomes in the PANTHER database.
        """
        suburl = "/services/oai/pantherdb/supportedgenomes"
        url = self.baseurl + suburl
        response = requests.get(url)
        if response.ok:
            response_dat = response.json()
            return response_dat["search"]['output']['genomes']['genome']
        else:
            raise Exception("Error: {}".format(response.status_code))  

@click.command()
@click.option('--seconds', default=1, help='Seconds parameter.')
@click.option('--taxonid', default='9606', help='Taxon ID.')
@click.option('--datasetid', default='GO:0008150', help='Dataset ID.')
@click.option('--outputfile', default='output.json', help='Output file.')
@click.option('--gene_input_list', default='input.txt', help='Gene input list.')
@click.option('--test_type', default='FISHER', help='Test type.')
@click.option('--correction', default='FDR', help='Correction.')
def main(seconds, taxonid, datasetid, outputfile, gene_input_list, test_type, correction):
    params_seconds = seconds
    params_taxonid = taxonid
    params_datasetid = datasetid
    params_outputfile = outputfile
    params_gene_input_list = gene_input_list
    params_test_type = test_type
    params_correction = correction

    with open(params_gene_input_list, "r") as f:
        genes_input = []
        for line in f:
            genes_input.append(line.strip())
    
    
    if len(genes_input) > 100000:
        raise Exception("Error: Input list contains more than 100000 genes, not supported by the API.")
    else:
        genes_input_str = ",".join(genes_input)

    api = PantherAPI()
    time.sleep(params_seconds)
    genomes = api.get_list_of_available_genomes()
    genomes_id = datasets_id = [str(i["taxon_id"]) for i in genomes]
    time.sleep(params_seconds)
    datasets = api.get_supportedannotdatasets()
    datasets_id = [str(i["id"]) for i in datasets]
    #pdb.set_trace()
    if params_taxonid not in genomes_id:
        raise Exception("Error: Taxon ID not found.")
    
    if params_datasetid not in datasets_id:
        raise Exception("Error: Dataset ID not found.")
    
    enrichment_results = api.get_enrichment(
                        gene_input_list=genes_input_str,
                        organism= params_taxonid,
                        annotation_data_set = params_datasetid,
                        enrichment_test_type=params_test_type,
                        correction=params_correction)
    
    json.dump(enrichment_results,
              open(params_outputfile, "w"),
              indent=4)


if __name__ == "__main__":
    main()

