from django.db import models

class Bill(models.Model):
    bill_number = models.CharField(max_length=20)
    title = models.TextField()
    parliament_number = models.IntegerField()
    session_number = models.IntegerField()
    bill_type = models.CharField(max_length=50)
    status = models.CharField(max_length=100)
    introduced_date = models.DateField()
    royal_assent_date = models.DateField(null=True, blank=True)
    full_text_link = models.URLField()

    def __str__(self):
        return f"{self.bill_number} - {self.title}"

class Voting(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='votings')
    total_yeas = models.IntegerField()
    total_nays = models.IntegerField()
    total_abstain = models.IntegerField()
    vote_date = models.DateField()

    def __str__(self):
        return f"Voting for {self.bill.bill_number} on {self.vote_date}"

class Sponsor(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='sponsors')
    sponsor_id = models.CharField(max_length=100, unique=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sponsor for {self.bill.bill_number}"

class Senator(models.Model):
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=50)
    appointed_date = models.DateField()
    political_affiliation = models.CharField(max_length=100)
    contact_info = models.TextField()

    def __str__(self):
        return f"Senator {self.name} from {self.province}"