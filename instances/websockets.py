#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gevent
import random
import traceback
import json
from itertools import chain
from gevent.coros import Semaphore
from datetime import datetime
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin


POSITIVE_WORDS = list(chain(*filter(bool, map(lambda s: s.split(), """
Absolutely Absorbing Abundance Ace Active Admirable Adore Agree Alert
A1 Alive Amazing Appealing Approval Aroma Attraction Award Bargain
Beaming Beats Beautiful Best Better Bits Boost Bounce Breakthrough
Breezy Brief Bright Brilliant Brimming Buy Care Certain Charming Chic
Choice Clean Clear Colourful Comfy Compliment Confidence Connoisseur
Cool Courteous Coy Creamy Crisp Cuddly Dazzling Debonair Delicate
Delicious Delightful Deluxe Dependable Desire Diamond Difference
Dimple Discerning Distinctive Divine Dreamy Drool Dynamic Easy Economy
Ecstatic Effervescent Efficient Endless Energy Enhance Enjoy Enormous
Ensure Enticing Essence Essential Exactly Excellent Exceptional
Exciting Exclusive Exhilaration Exotic Expert Exquisite Extol Extra
Eye-catching Fabled Fair Famous Fantastic Fashionable Fascinating Fab
Fast Favourite Fetching Finest Finesse First Fizz Flair Flattering
Flip Flourishing Foolproof Forever Fragrance Free Freshness Friendly
Full Fun Galore Generous Genius Gentle Giggle Glamorous Glitter
Glorious Glowing Go-ahead Golden Goodness Gorgeous Graceful Grand
Great Guaranteed Happy Healthy Heartwarming Heavenly Ideal Immaculate
Impressive Incredible Inspire Instant Interesting Invigorating
Invincible Inviting Irresistible Jewel Joy Juicy Keenest Kind Kissable
K.O. Know-how Leads Legend Leisure Light Lingering Logical Longest
Lovely Lucky Luscious Luxurious Magic Matchless Magnifies it Maxi
Memorable Mighty Miracle Modern More Mouthwatering Multi Munchy
Natural Need New Nice Nutritious O.K. Opulent Outlasts Outrageous
Outstanding Palate Palatial Paradise Pamper Passionate Peak Pearl
Perfect Pick-me-up Pleasure Pleases Plenty Plum Plump Plus Popular
Positive Power Precious Prefer Prestige Priceless Pride Prime Prize
Protection Proud Pure Quality Quantity Quenching Quick Quiet Radiant
Ravishing Real Reap Recommendation Refined Refreshing Relax Reliablel
Renowned Reputation Rest Rewarding Rich Right Rosy Royal Safety Save
Satisfaction Scores Seductive Select Sensitive Sensational Serene
Service Sexy Shapely Share Sheer Shy Silent Silver Simple Singular
Sizzling Skilful Slick Smashing Smiles Solar Smooth Soft Sound
Sparkling Special Spectacular Speed Spicy Splendid Spice Spotless
Spruce Star Strong Stunning Stylish Subtle Success Succulent Sun
Superb Superlative Supersonic Supreme Sure Sweet Swell Symphony Tan
Tangy Tasty Tempting Terrific Thoroughbred Thrilling Thriving Timeless
Tingle Tiny Top Totally Traditional Transformation Treat Treasure
Trendy True Trust Ultimate Ultra Unbeatable Unblemished Undeniably
Undoubtedly Unique Unquestionnably Unrivalled Unsurpassed Valued
Valuable Vanish Varied Versatile Victor Vigorous Vintage V.I.P.  Vital
Vivacious Warm Wealth Wee Whiz Whole Whopper Winner Wise Wonderful
Worthy Wow! Youthful Yule Young Zap Zeal Zest Zip Zoom 101 1990s 20th
Century""".splitlines()))))


class InstancesBroadcaster(BaseNamespace, BroadcastMixin):
    def __init__(self, *args, **kw):
        super(InstancesBroadcaster, self).__init__(*args, **kw)
        self.app = Semaphore()
        self.app.acquire()

    def should_live(self):
        return self.app.locked()

    def humanized_now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def serialize(self, data):
        return json.dumps(data)

    def format_exception(self, exc):
        if exc:
            return traceback.format_exc(exc)

        return ''

    def broadcast_status(self, text, error=None):
        traceback = self.format_exception(error)
        css_class = error and 'error' or 'success'

        payload = self.serialize({
            'text': text,
            'traceback': traceback,
            'ok': not error,
            'when': self.humanized_now(),
            'class': css_class
        })
        self.broadcast_event('status', payload)
        if error:
            gevent.sleep(30)


class StatsBroadcaster(InstancesBroadcaster):
    def random_status(self):
        while self.should_live():
            self.broadcast_status("Instances is running {0}!".format(random.choice(POSITIVE_WORDS)))
            gevent.sleep(.3)

    def on_listen(self, msg):
        workers = [
            self.spawn(self.random_status),
        ]
        gevent.joinall(workers)


NAMESPACES = {"": StatsBroadcaster}
