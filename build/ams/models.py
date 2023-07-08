from django.db import models

# Create your models here.
class Credentials(models.Model):
    username=models.CharField(max_length=255,primary_key=True)
    password=models.CharField(max_length=255)
class Attendance(models.Model):
    date=models.CharField(max_length=255,primary_key=True)
    N181022=models.CharField(max_length=255)
    N180789=models.CharField(max_length=255)
    N180792=models.CharField(max_length=255)
    N180924=models.CharField(max_length=255)
    N180825=models.CharField(max_length=255)
    N170976=models.CharField(max_length=255)
class e2csecse2(models.Model):
    date=models.CharField(max_length=255,primary_key=True)
    N200037=models.CharField(max_length=255)
    N200377=models.CharField(max_length=255)
    N200381=models.CharField(max_length=255)
    N200392=models.CharField(max_length=255)
    N200491=models.CharField(max_length=255)
    N200517=models.CharField(max_length=255)
    N200539=models.CharField(max_length=255)
    N200542=models.CharField(max_length=255)
    N200572=models.CharField(max_length=255)
    N200575=models.CharField(max_length=255)
    N200594=models.CharField(max_length=255)
    N200680=models.CharField(max_length=255)
    N200689=models.CharField(max_length=255)
    N200695=models.CharField(max_length=255)
    N200745=models.CharField(max_length=255)
    N200770=models.CharField(max_length=255)
    N200814=models.CharField(max_length=255)
    N200829=models.CharField(max_length=255)
    N200841=models.CharField(max_length=255)
    N200883=models.CharField(max_length=255)
    N200910=models.CharField(max_length=255)
    N200947=models.CharField(max_length=255)
    N200948=models.CharField(max_length=255)
    N200957=models.CharField(max_length=255)
    N201006=models.CharField(max_length=255)
    N201014=models.CharField(max_length=255)
    N201045=models.CharField(max_length=255)
    N201050=models.CharField(max_length=255)
    N201056=models.CharField(max_length=255)
    N201064=models.CharField(max_length=255)
    N201070=models.CharField(max_length=255)


# def add_dynamic_field(model_class, field_name, field):
#     """
#     Dynamically add a field to a Django model.
#     """
#     model_class.add_to_class(field_name, field)

# # Usage example
# add_dynamic_field(First, 'loverboy', models.CharField(max_length=255,null=True))