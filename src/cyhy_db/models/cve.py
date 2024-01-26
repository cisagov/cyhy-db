# Third-Party Libraries
from mongoengine import Document, FloatField, IntField, StringField


class CVE(Document):
    id = StringField(primary_key=True)
    cvss_score = FloatField(min_value=0.0, max_value=10.0)
    cvss_version = StringField(choices=["2.0", "3.0", "3.1"])
    severity = IntField(choices=[1, 2, 3, 4], default=1)

    meta = {"collection": "cves"}

    def calculate_severity(self):
        if self.cvss_version == "2.0":
            if self.cvss_score == 10:
                self.severity = 4
            elif self.cvss_score >= 7.0:
                self.severity = 3
            elif self.cvss_score >= 4.0:
                self.severity = 2
            else:
                self.severity = 1
        else:  # CVSS versions 3.0 or 3.1
            if self.cvss_score >= 9.0:
                self.severity = 4
            elif self.cvss_score >= 7.0:
                self.severity = 3
            elif self.cvss_score >= 4.0:
                self.severity = 2
            else:
                self.severity = 1

    def save(self, *args, **kwargs):
        self.calculate_severity()
        return super().save(*args, **kwargs)
