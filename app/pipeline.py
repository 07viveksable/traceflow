import csv
import uuid
from pathlib import Path

from app.logger import logger
from app.config import load_config
from app.validator import validate_data

BASE_DIR = Path(__file__).resolve().parent.parent


class TraceFlowPipeline:

    def __init__(self, config):

        self.config = config

        self.run_id = str(uuid.uuid4())

        self.input_file = (
            BASE_DIR / config["input_file"]
        )

        self.output_file = (
            BASE_DIR / config["output_file"]
        )

        self.tax_rate = config["tax_rate"]

    def extract(self):

        logger.info(
            "[%s] Starting data extraction",
            self.run_id
        )

        data = []

        with open(self.input_file, "r") as file:

            reader = csv.DictReader(file)

            for row in reader:
                data.append(row)

        logger.info(
            "[%s] Data extraction completed. Records: %s",
            self.run_id,
            len(data)
        )

        return data

    def validate(self, data):

        logger.info(
            "[%s] Starting data validation",
            self.run_id
        )

        validate_data(data)

        logger.info(
            "[%s] Data validation successful",
            self.run_id
        )

    def transform(self, data):

        logger.info(
            "[%s] Starting data transformation",
            self.run_id
        )

        for row in data:

            row["amount"] = float(row["amount"])

            row["final_amount"] = round(
                row["amount"] *
                (1 + self.tax_rate),2
            )

        logger.info(
            "[%s] Data transformation completed",
            self.run_id
        )

        return data

    def load(self, data):

        logger.info(
            "[%s] Starting data loading",
            self.run_id
        )

        fieldnames = [
            "id",
            "name",
            "city",
            "product",
            "amount",
            "final_amount",
            "status"
        ]

        with open(
            self.output_file,
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            writer.writerows(data)

        logger.info(
            "[%s] Data loading completed",
            self.run_id
        )

    def run(self):

        logger.info(
            "[%s] ========== PIPELINE STARTED ==========",
            self.run_id
        )

        try:

            data = self.extract()

            self.validate(data)

            data = self.transform(data)

            self.load(data)

            logger.info(
                "[%s] ========== PIPELINE COMPLETED SUCCESSFULLY ==========",
                self.run_id
            )

        except Exception as error:

            logger.exception(
                "[%s] PIPELINE FAILED: %s",
                self.run_id,
                error
            )


if __name__ == "__main__":

    config = load_config()

    pipeline = TraceFlowPipeline(config)

    pipeline.run()