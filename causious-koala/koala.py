import sys
from urllib.request import urlopen
from urllib import error
import getopt
import csv
import asyncio
from statistics import mean 
from collections import defaultdict
import logging

import aiofiles
import aiohttp
from aiohttp import ClientSession, TCPConnector, ClientTimeout
from bs4 import BeautifulSoup
import textstat
import gspread
from oauth2client.service_account import ServiceAccountCredentials


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("koala")
logging.getLogger("chardet.charsetprober").disabled = True
CONTACT_DB_SHEET_NAME = 'Contact Database'
PP_SPREADSHEET_NAME = 'Privacy Score Data'
CREDENTIALS_FILE = 'koala-creds.json'
MAX_DOMAIN_RANK = 100
PP_WORKSHEET_NAME = "Privacy Policies"


class ScorePP(object):
	"""Creates a list of Privacy Policy URLs, Downloads content and scores"""
	scope = ['https://spreadsheets.google.com/feeds',
		     'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
	gc = gspread.authorize(credentials)


	def getTextFromHTML(self, html):	
		soup = BeautifulSoup(html, features="lxml")

		# kill all script and style elements
		for script in soup(["script", "style"]):
		    script.extract()    # rip it out

		# get text
		text = soup.get_text()

		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in text.splitlines())
		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		# drop blank lines
		text = '\n'.join(chunk for chunk in chunks if chunk)

		return text

	def testTestReadability(self, text):
		# 1 good 10 bad (https://pypi.org/project/textstat/)
		return textstat.smog_index(text)

	def getDomainList(self):
		logger.info("Loading sheets...")
		contacts_sheet = self.gc.open(CONTACT_DB_SHEET_NAME).sheet1
		pp_sheet = self.gc.open(PP_SPREADSHEET_NAME).worksheet(PP_WORKSHEET_NAME)
		contacts_list = contacts_sheet.get_all_records()
		pp_list = pp_sheet.get_all_records()
		logger.info("Sheets loaded.")

		combined_list = {row['Domain']:[row['Privacy Policy']] for row in contacts_list if len(row['Privacy Policy'])>0}

		for row in pp_list:
			domain = row['Domain']
			pp_url = row['Privacy Policy']
			if domain in combined_list:
				if pp_url not in combined_list[domain]:
					combined_list[domain].append(pp_url)
			else:
				combined_list[domain] = [pp_url]
		return combined_list

	def loadTopSitesLookup(self, topSitesFile):
		results = {}
		logger.info("Loading top sites...")
		with open(topSitesFile) as csvfile:
			reader = csv.DictReader(csvfile)
			for line in reader:
				results[line['Domain']] = line['GlobalRank']
		logger.info("Top sites loaded.")
		return results

	async def fetch_html(self, url, session, **kwargs):
	    resp = await session.request(method="GET", url=url, allow_redirects=True, **kwargs)
	    resp.raise_for_status()
	    logger.info("Got response [%s] for URL: %s", resp.status, url)
	    html = await resp.text()
	    return html

	async def parse(self, urls, session, **kwargs):
	    combined_text = ""
	    for url in urls:
		    try:
		        html = await self.fetch_html(url, session, **kwargs)
		        combined_text = combined_text + self.getTextFromHTML(html)
		    except (
		        aiohttp.ClientError,
		        aiohttp.http_exceptions.HttpProcessingError,
		    ) as e:
		        logger.error(
		            "aiohttp exception for %s [%s]: %s",
		            url,
		            getattr(e, "status", None),
		            str(e),
		        )
		    except Exception as e:
		    	logger.exception("Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {}))
		    return combined_text

	async def score(self, urls, session, **kwargs):
		text = await self.parse(urls, session, **kwargs)
		return self.testTestReadability(text)		

	async def write_one(self, file, domain, rank, urls, session, **kwargs):
	    score = await self.score(urls, session, **kwargs)
	    async with aiofiles.open(file, "a") as f:
	    	joined_urls = ";".join(urls)
	    	await f.write(f"{domain},{rank},{score},{joined_urls}\n")
	    	logger.info("Wrote results for %s", domain)

	async def bulk_crawl_and_write(self, file, site_rank, domain_list, **kwargs):
		async with ClientSession(
				connector=TCPConnector(verify_ssl=False),
				timeout=ClientTimeout(total=60)
			) as session:
			tasks = []
			for domain, urls in domain_list.items():
				if domain in site_rank and int(site_rank[domain]) < MAX_DOMAIN_RANK:
					logger.info("Scheduling work for %s", domain)
					tasks.append(asyncio.create_task(
						self.write_one(file, domain, site_rank[domain], urls, session, **kwargs)))
			await asyncio.gather(*tasks)

	def run(self, topsitefile, outputfile):
		site_rank = self.loadTopSitesLookup(topsitefile)
		domain_list = self.getDomainList()
		with open(outputfile, "w") as outfile:
			outfile.write("domain,majestic_rank,redability_score,urls\n")
		asyncio.run(self.bulk_crawl_and_write(outputfile, site_rank, domain_list))


def getArgs():
	usage = 'koala.py -s <topsitefile> -o <outputfile>'
	topsitefile = ''
	outputfile = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hs:o:",["sfile=", "ofile="])
	except getopt.GetoptError:
		print(usage)
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print(usage)
			sys.exit()
		elif opt in ("-s", "--sfile"):
			topsitefile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg
	if not topsitefile or not outputfile:
		print(usage)
		sys.exit(2)
	return topsitefile, outputfile


if __name__ == '__main__':
	assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
	spp = ScorePP()
	spp.run(*getArgs())







