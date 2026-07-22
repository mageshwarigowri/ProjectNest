from django.contrib.auth.models import User
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart, Order, Profile, Wishlist

@receiver(post_save, sender=User)
def provision_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Cart.objects.create(user=instance)
        Wishlist.objects.create(user=instance)

@receiver(post_save, sender=Order)
def award_delivery_coins(sender, instance, **kwargs):
    if instance.status == "delivered" and instance.user_id and instance.coins_earned == 0:
        earned = int(instance.subtotal // 100)
        if earned:
            Order.objects.filter(pk=instance.pk, coins_earned=0).update(coins_earned=earned)
            Profile.objects.filter(user_id=instance.user_id).update(reward_coins=F("reward_coins") + earned)
