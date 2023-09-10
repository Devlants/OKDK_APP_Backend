from django.db import models
import re

class Membership(models.Model):
    user = models.ForeignKey("account.User",on_delete=models.CASCADE)
    brand = models.ForeignKey("coffee.Brand",on_delete=models.CASCADE)
    serial_num = models.CharField(max_length=100)
    point = models.IntegerField(default = 0)
    image = models.ImageField(upload_to="membership")

class History(models.Model):
    membership = models.ForeignKey(Membership,on_delete=models.CASCADE)
    point = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=100)
    cur_total = models.IntegerField(default=0)

    def use_point(self):
        self.membership.point -= self.point
        self.membership.save()
        return self.membership.point

    def save_point(self):
        self.membership.point += self.point
        self.membership.save()
        return self.membership.point

class Card(models.Model):
    user = models.ForeignKey("account.User",on_delete=models.CASCADE)
    image = models.ImageField(upload_to="card",null = True)
    serial_num = models.CharField(max_length=100)
    expiry_date = models.CharField(max_length=100)
    cvc = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    default = models.BooleanField(default = False)
    regex_patterns = {
        r"^3560[0-9]*": "BC",
        r"^3562 96[0-9]*": "신한",
        r"^3562 97[0-9]*": "신한",
        r"^3563 16[0-9]*": "농협",
        r"^3563 17[0-9]*": "농협",
        r"^3563 \d\d[0-9]*": "BC",
        r"^3565[0-9]*": "BC",
        r"^3568 00[0-9]*": "외환",
        r"^3568 01[0-9]*": "외환",
        r"^3568 02[0-9]*": "외환",
        r"^3568 03[0-9]*": "외환",
        r"^3568 20[0-9]*": "BC",
        r"^3569 00[0-9]*": "신한",
        r"^3569 01[0-9]*": "신한",
        r"^3569 02[0-9]*": "신한",
        r"^3569 10[0-9]*": "국민",
        r"^3569 11[0-9]*": "국민",
        r"^3569 12[0-9]*": "국민",
        r"^3569 14[0-9]*": "롯데",
        r"^3569 15[0-9]*": "롯데",
        r"^3569 16[0-9]*": "롯데",
        r"^3616[0-9]*": "현대",
        r"^3710 01[0-9]*": "외환",
        r"^3710 02[0-9]*": "외환",
        r"^3710 03[0-9]*": "외환",
        r"^3747 22[0-9]*": "외환",
        r"^3747 23[0-9]*": "외환",
        r"^3747 24[0-9]*": "외환",
        r"^3751 44[0-9]*": "국민",
        r"^3759 87[0-9]*": "삼성",
        r"^3762 72[0-9]*": "롯데",
        r"^3762 77[0-9]*": "롯데",
        r"^3763 64[0-9]*": "국민",
        r"^3779 73[0-9]*": "롯데",
        r"^3779 81[0-9]*": "신한",
        r"^3779 82[0-9]*": "신한",
        r"^3779 89[0-9]*": "삼성",
        r"^3791 83[0-9]*": "삼성",
        r"^3791 92[0-9]*": "하나",
        r"^3791 93[0-9]*": "하나",
        r"^4450[0-9]*": "VISA",
        r"^4023 67[0-9]*": "하나",
        r"^4028 57[0-9]*": "현대",
        r"^4046 78[0-9]*": "BC",
        r"^4048 25[0-9]*": "BC",
        r"^4057 53[0-9]*": "신한",
        r"^4063 57[0-9]*": "씨티",
        r"^4101 09[0-9]*": "씨티",
        r"^4119 00[0-9]*": "외환",
        r"^4119 04[0-9]*": "외환",
        r"^4119 05[0-9]*": "하나",
        r"^4140 25[0-9]*": "하나",
        r"^4181 23[0-9]*": "현대",
        r"^4182 36[0-9]*": "외환",
        r"^4214 17[0-9]*": "수협",
        r"^4214 18[0-9]*": "수협",
        r"^4214 20[0-9]*": "BC",
        r"^4214 68[0-9]*": "롯데",
        r"^4221 90[0-9]*": "수협",
        r"^4227 27[0-9]*": "BC",
        r"^4324 45[0-9]*": "수협",
        r"^4330 28[0-9]*": "현대",
        r"^4349 75[0-9]*": "신한",
        r"^4364 20[0-9]*": "신한",
        r"^4386 76[0-9]*": "신한",
        r"^4400 25[0-9]*": "BC",
        r"^4404 46[0-9]*": "씨티",
        r"^4432 33[0-9]*": "LG",
        r"^4473 20[0-9]*": "BC",
        r"^4481[0-9]*": "BC",
        r"^4499 14[0-9]*": "신한",
        r"^4512 45[0-9]*": "삼성",
        r"^4512 81[0-9]*": "현대",
        r"^4518 42[0-9]*": "신한",
        r"^4518 45[0-9]*": "신한",
        r"^4553[0-9]*": "BC",
        r"^4554 37[0-9]*": "외환",
        r"^4570 47[0-9]*": "하나",
        r"^4579 72[0-9]*": "국민",
        r"^4579 73[0-9]*": "국민",
        r"^4585 32[0-9]*": "삼성",
        r"^4599 00[0-9]*": "외환",
        r"^4599 30[0-9]*": "외환",
        r"^4599 50[0-9]*": "외환",
        r"^4599 52[0-9]*": "광주",
        r"^4628 90[0-9]*": "씨티",
        r"^4639 16[0-9]*": "제주",
        r"^4649 59[0-9]*": "롯데",
        r"^4658 87[0-9]*": "신한",
        r"^4658 89[0-9]*": "수협",
        r"^4705 87[0-9]*": "삼성",
        r"^4705 88[0-9]*": "삼성",
        r"^4743 60[0-9]*": "씨티",
        r"^4854 79[0-9]*": "농협",
        r"^4902 20[0-9]*": "BC",
        r"^4906[0-9]*": "BC",
        r"^5021 23[0-9]*": "국민",
        r"^5107 37[0-9]*": "신한",
        r"^5124 62[0-9]*": "롯데",
        r"^5148 76[0-9]*": "씨티",
        r"^5155 94[0-9]*": "신한",
        r"^5165 74[0-9]*": "하나",
        r"^5238 30[0-9]*": "외환",
        r"^5240 40[0-9]*": "농협",
        r"^5240 41[0-9]*": "농협",
        r"^5241 44[0-9]*": "씨티",
        r"^5243 33[0-9]*": "현대",
        r"^5243 35[0-9]*": "외환",
        r"^5243 53[0-9]*": "외환",
        r"^5310 80[0-9]*": "삼성",
        r"^5318 38[0-9]*": "하나",
        r"^5350 20[0-9]*": "우리",
        r"^5387 20[0-9]*": "BC",
        r"^5388[0-9]*": "BC",
        r"^5389 20[0-9]*": "우리",
        r"^5404 47[0-9]*": "삼성",
        r"^5409 26[0-9]*": "국민",
        r"^5409 47[0-9]*": "국민",
        r"^5421 58[0-9]*": "신한",
        r"^5428 79[0-9]*": "신한",
        r"^5433 33[0-9]*": "현대",
        r"^5462 52[0-9]*": "하나",
        r"^5520 70[0-9]*": "삼성",
        r"^5522 20[0-9]*": "우리",
        r"^5522 90[0-9]*": "현대",
        r"^5523 77[0-9]*": "현대",
        r"^5525 76[0-9]*": "신한",
        r"^5543 46[0-9]*": "국민",
        r"^5585 26[0-9]*": "국민",
        r"^6060 52[0-9]*": "은련",
        r"^6210[0-9]*": "BC",
        r"^6251 04[0-9]*": "롯데",
        r"^6253[0-9]*": "BC",
        r"^6258 04[0-9]*": "국민",
        r"^6259 04[0-9]*": "롯데",
        r"^6541[0-9]*": "BC",
        r"^6556[0-9]*": "BC",
        r"^9000[0-9]*": "직불",
        r"^9400 10[0-9]*": "씨티",
        r"^9407 01[0-9]*": "수협",
        r"^9407 02[0-9]*": "수협",
        r"^9409 15[0-9]*": "롯데",
        r"^9409 51[0-9]*": "롯데",
        r"^9410 61[0-9]*": "신한",
        r"^9410 83[0-9]*": "신한",
        r"^9410 90[0-9]*": "삼성",
        r"^9410[0-9]*": "BC",
        r"^9411 61[0-9]*": "신한",
        r"^9420 61[0-9]*": "신한",
        r"^9420 90[0-9]*": "삼성",
        r"^9420[0-9]*": "BC",
        r"^9430[0-9]*": "BC",
        r"^9436 45[0-9]*": "국민",
        r"^9440[0-9]*": "BC",
        r"^9441 16[0-9]*": "농협",
        r"^9445 20[0-9]*": "BC",
        r"^9445 41[0-9]*": "국민",
        r"^9445 42[0-9]*": "국민",
        r"^9445 47[0-9]*": "국민",
        r"^9460[0-9]*": "BC",
        r"^9461[0-9]*": "BC",
        r"^9490 13[0-9]*": "현대",
        r"^9490 28[0-9]*": "현대",
        r"^9490 [0-9]*": "국민",
        r"^9530 03[0-9]*": "광주",
        r"^5898[0-9]*": "직불",
        r"^5021 23[0-9]*": "국민",
        r"^5029 28[0-9]*": "하나",
        r"^5886 44[0-9]*": "씨티",
        r"^6048[0-9]*": "BC",
        r"^6060[0-9]*": "신한",
        r"^6360[0-9]*": "BC",
        r"^6361 89[0-9]*": "하나",

    }

    def check_string_with_regex(self,input_string):
        for pattern, value in self.regex_patterns.items():
            result = re.match(pattern, input_string)
            if result:
                return value

        return "알수없음"

    def __str__(self):
        return self.check_string_with_regex(self.serial_num) + " ("+self.serial_num[15:]+")"

    def set_default(self):
        cards = self.user.card_set.filter(default = True)
        for card in cards:
            card.default=False
            card.save()
        self.default=True
        return
