import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult


load_dotenv("config/.env")

PTH_LOG = Path(os.getenv("PTH_LOG", "logs"))
PTH_PDF = Path(os.getenv("PTH_PDF", "data/pdf"))
PTH_ZIP = Path(os.getenv("PTH_ZIP", "data/zip"))

logging.basicConfig(
    filename=PTH_LOG / "Extractor.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class Extractor:
    def __init__(self) -> None:
        """
        Defines Adobe PDF service instance; and a list of PDFs to be extracted.
        """
        PTH_ZIP.mkdir(parents=True, exist_ok=True)
        
        credentials = ServicePrincipalCredentials(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
        )
        
        self.pdf_services = PDFServices(credentials=credentials)
        
        self.outstanding_pdfs = self._get_outstanding_pdf()
    
    def _get_outstanding_pdf(self) -> set:
        """
        Find out a list of PDFs that have not been processed to ZIPs.
        
        Returns:
            A set of unprocessed PDFs.
        """
        pdfs = {file.stem for file in PTH_PDF.glob("*.pdf")}
        zips = {file.stem for file in PTH_ZIP.glob("*.zip")}
        
        return pdfs - zips
    
    def _extract_table_from_pdf(self, ctn: str) -> None:
        """
        Extracts tables from a single CTN.
        
        Args:
            ctn: PDF file name to be processed.
        
        Raises:
            Either quota is not available or free tier quota is exhausted.
        """
        try:
            with open(PTH_PDF / f"{ctn}.pdf", "rb") as file:
                input_stream = file.read()
            
            input_asset = self.pdf_services.upload(
                input_stream=input_stream,
                mime_type=PDFServicesMediaType.PDF,
            )
            
            extract_pdf_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TABLES],
            )
            
            job_extract = ExtractPDFJob(
                input_asset=input_asset,
                extract_pdf_params=extract_pdf_params,
            )
            
            location = self.pdf_services.submit(job_extract)
            response = self.pdf_services.get_job_result(
                location,
                ExtractPDFResult,
            )
            
            asset_result = response.get_result().get_resource()
            asset_stream = self.pdf_services.get_content(asset_result)
            
            with open(PTH_ZIP / f"{ctn}.zip", "wb") as file:
                file.write(asset_stream.get_input_stream())
            
        except Exception as e:
            logging.warning(f"Failed to extract table from {ctn}: {str(e)}")
    
    def extract_table(self) -> None:
        """
        Extracts tables from outstanding CTN.
        """
        for idx, pdf in enumerate(self.outstanding_pdfs):
            if idx % 50 == 0:
                cnt = len(self.outstanding_pdfs) - idx
                logging.info(f"- Pending {cnt} PDFs to be extracted.")
            
            self._extract_table_from_pdf(pdf)


if __name__ == "__main__":
    Extractor().extract_table()
