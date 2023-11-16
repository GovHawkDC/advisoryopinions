from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json, config
from datetime import datetime
import hashlib
import os
from typing import List
from marshmallow import fields


@dataclass_json
@dataclass
class Attachment:
    title: str
    url: str
    mimetype: str


@dataclass_json
@dataclass
class AdvisoryOpinion:
    agency: str
    agency_short: str
    identifier: str
    published: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )
    title: str
    url: str
    attachments: List[Attachment] = field(default_factory=list)
    classification: str = "advisory-opinion"
    subagency: str = ""
    summary: str = ""

    def add_attachment(self, title, url, mimetype) -> None:
        # sure this shouldn't be "self._package.append(param)"?
        attachment = Attachment(title, url, mimetype)
        self.attachments.append(attachment)

    def __repr__(self):
        return f"{self.agency_short} - {self.published.strftime('%Y-%m-%d')} {self.identifier} {self.title.strip()}"

    def save(self) -> bool:
        date = self.published.strftime("%Y-%m-%d")

        if self.identifier == "":
            if self.url.strip() == "":
                raise Exception(f"Invalid URL: {self.url}")
            self.identifier = hashlib.sha256(self.url.encode("utf-8")).hexdigest()
        
        self.identifier = self.identifier.strip().replace(" ", "-")
        self.identifier = f"{self.agency_short}-{self.identifier}"

        path = f"data/{self.agency_short}/"
        filename = f"{path}/{date}-{self.identifier}.json"

        if not os.path.exists(path):
            os.makedirs(path)

        if not os.path.isfile(filename):
            with open(filename, "w") as f:
                f.write(self.to_json())
                return True
        return False
