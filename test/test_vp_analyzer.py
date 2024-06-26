from collections import Counter
from scipy.misc import comb
import unittest
from vp_analyzer import HandAnalyzer, DiscardValue


class Test_vp_analyzer(unittest.TestCase):
    def setUp(self):
        self.h1 = HandAnalyzer("ahjcts7s4h")
        self.h2 = HandAnalyzer("qd9c8d5c2c")
        self.h3 = HandAnalyzer("qd9c8dacad")
        self.junk = HandAnalyzer("ts9c8d5c2h")

        self.aces8s_d = {
            "pair_jqka": 1,
            "two_pair": 2,
            "three_kind": 3,
            "straight": 4,
            "flush": 5,
            "full_house": 8,
            "four_kind": 25,
            "four_kind7": 50,
            "four_kindA8": 80,
            "straight_flush": 50,
            "royal_flush": 800,
        }

        self.tripbonusplus_d = {
            "pair_jqka": 1,
            "two_pair": 1,
            "three_kind": 3,
            "straight": 4,
            "flush": 5,
            "full_house": 9,
            "four_kind": 50,
            "four_kind234": 120,
            "four_kindA": 240,
            "straight_flush": 100,
            "royal_flush": 800,
        }

    # TODO: test count_wins (currently tested indirectly via HandAnalyzer.analyze)

    def test_hold(self):
        h1 = HandAnalyzer("ahjcts7s4h")
        hold_d_h1AJ = {
            "d": [("T", "s"), ("7", "s"), ("4", "h")],
            "h": [("A", "h"), ("J", "c")],
        }
        hold_d = h1.hold([True] * 2 + [False] * 3)
        self.assertEqual(hold_d, hold_d_h1AJ)

    def test_analyze(self):
        # based on results from: https://www.videopokertrainer.org/calculator/
        junk_plays = self.junk.analyze()
        disc_all = "X" * 10
        exp_val_discardjunk = junk_plays[disc_all]["expected_val"]
        self.assertEqual(round(exp_val_discardjunk, 5), round(0.35843407071, 5))

        exp_val_holdt = junk_plays["TsXXXXXXXX"]["expected_val"]
        self.assertEqual(round(exp_val_holdt, 5), round(0.32971715302, 5))

        h2_plays = self.h2.analyze()
        exp_val_holdq = h2_plays["QdXXXXXXXX"]["expected_val"]
        self.assertEqual(round(exp_val_holdq, 5), round(0.4741961707734, 5))

        h2_plays_bdc = self.h2.analyze(
            return_full_analysis=False, return_bestdisc_cnts=True
        )

        h2_bdc_out = {
            "QdXXXXXXXX": {
                "full_house": 288.0,
                "three_kind": 4102.0,
                "four_kind": 52.0,
                "straight": 590,
                "straight_flush": 1,
                "royal_flush": 1,
                "expected_val": 0.47419617077341408,
                "flush": 328.0,
                "pair_jqka": 45456.0,
                "two_pair": 8874.0,
            }
        }
        self.assertEqual(h2_plays_bdc, h2_bdc_out)

        exp_val_holdq8 = h2_plays["QdXX8dXXXX"]["expected_val"]
        self.assertEqual(round(exp_val_holdq8, 5), round(0.41036077705827, 5))

        h3_plays = self.h3.analyze()
        exp_val_holdaa = h3_plays["XXXXXXAcAd"]["expected_val"]
        self.assertEqual(round(exp_val_holdaa, 5), round(1.536540240518, 5))

        exp_val_holdaa8 = h3_plays["XXXX8dAcAd"]["expected_val"]
        self.assertEqual(round(exp_val_holdaa8, 5), round(1.4162812210915, 5))

        lowp = HandAnalyzer("qcjckdtdth").analyze()
        exp_val_qjkt = lowp["QcJcKdTdXX"]["expected_val"]
        self.assertEqual(round(exp_val_qjkt, 5), round(0.8723404255319, 5))

        h2A8 = HandAnalyzer("".join(self.h2.hand), payouts=self.aces8s_d)
        h2A8_plays = h2A8.analyze()
        exp_val_h2A8 = h2A8_plays["QdXXXXXXXX"]["expected_val"]
        self.assertEqual(round(exp_val_h2A8, 5), round(0.47119109690802569, 5))

        junk6 = HandAnalyzer("tc9d6h5s2c", payouts=self.aces8s_d)
        j6_plays = junk6.analyze()
        exp_val_j6 = j6_plays[disc_all]["expected_val"]
        j6_disc_ev = 0.3588441261353939
        self.assertEqual(round(exp_val_j6, 5), round(j6_disc_ev, 5))
        j6_best = junk6.analyze(return_full_analysis=False, return_bestdisc_cnts=False)
        self.assertEqual(j6_best[0], "".join(disc_all))
        self.assertEqual(round(j6_best[1], 5), round(j6_disc_ev, 5))

        aaa = HandAnalyzer("ACADAH9CQH", payouts=self.aces8s_d)
        aaa_best = aaa.analyze(return_full_analysis=False, return_bestdisc_cnts=False)
        self.assertEqual(aaa_best[0], "".join(("Ac", "Ad", "Ah", "XX", "XX")))
        self.assertEqual(round(aaa_best[1], 5), round(6.5818686401480111, 5))

    def test_pay_current_hand(self):
        for handobj in [self.h1, self.h2, self.junk]:
            self.assertEqual(handobj.pay_current_hand(), 0)

        fours_str = ["7c7h7d8s7s", "8c8d7h8h8s", "As7sAhAdAc", "QcQdQhQs2c"]
        for fks, pay in zip(fours_str, [50, 80, 80, 25]):
            self.assertEqual(HandAnalyzer(fks).pay_current_hand(), 25)
            foursA8 = HandAnalyzer(fks, payouts=self.aces8s_d)
            self.assertEqual(foursA8.pay_current_hand(), pay)

        normal_wins = [
            ("ackcqcjctc", 800),
            ("ac5c3c2c4c", 50),
            ("jc2cjd2djs", 9),
            ("7hKh9h4h2h", 6),
            ("Ac2d5d4d3d", 4),
            ("AcKdTdQdJd", 4),
            ("9h7c8sTcJc", 4),
            ("7c8h7h3s7s", 3),
            ("2c5d2h5s9c", 2),
            ("AcJc8s4dJd", 1),
            ("TsTdAs7c4h", 0),
        ]
        for hand, pay in normal_wins:
            self.assertEqual(HandAnalyzer(hand).pay_current_hand(), pay)

    def test_pivot_held_d(self):
        test_pivot = [("A", "J"), ("h", "c"), ("T", "7", "4"), ("s", "s", "h")]
        dv = DiscardValue(
            held_d={
                "d": [("T", "s"), ("7", "s"), ("4", "h")],
                "h": [("A", "h"), ("J", "c")],
            }
        )
        self.assertEqual(dv.pivot_held_d(), test_pivot)

        dv2 = DiscardValue(hand_str="ahjcts7s4h", hold_str="ahjcxxXXxx")
        self.assertEqual(dv2.pivot_held_d(), test_pivot)

    def test_royal_flush(self):
        h1aj = DiscardValue(held_d=self.h1.hold([True] * 2 + [False] * 3))
        self.assertEqual(h1aj.royal_flush(), 0)

        holda = DiscardValue(held_d=self.h1.hold([True] + [False] * 4))
        self.assertEqual(holda.royal_flush(), 1)

        discard_all = DiscardValue(held_d=self.h1.hold([False] * 5))
        self.assertEqual(discard_all.royal_flush(), 1)

        discard_h2 = DiscardValue(held_d=self.h2.hold([False] * 5))
        self.assertEqual(discard_h2.royal_flush(), 3)

    def test_three_kind(self):
        discard_h2 = DiscardValue(held_d=self.h2.hold([False] * 5))
        self.assertEqual(discard_h2.three_kind(), 31502)

        h3holdaa = DiscardValue(held_d=self.h3.hold([False] * 3 + [True] * 2))
        self.assertEqual(h3holdaa.three_kind(), 1854)

        h3hold8aa = DiscardValue(held_d=self.h3.hold([False] * 2 + [True] * 3))
        self.assertEqual(h3hold8aa.three_kind(), 84)

        # fh = HandAnalyzer('qdqcqh2s2d')
        # self.assertEqual(fh.three_kind(fh.hold([True]*5)), 0)
        # self.assertEqual(fh.three_kind(fh.hold([True]*3+[False]*2)), 968)
        holdfh = DiscardValue(hand_str="qdqcqh2s2d", hold_str="qdqcqh2s2d")
        self.assertEqual(holdfh.three_kind(), 0)
        qqq = DiscardValue(
            held_d=HandAnalyzer("qdqcqh2s2d").hold([True] * 3 + [False] * 2)
        )
        self.assertEqual(qqq.three_kind(), 968)

    def test_draw_for_ranks(self):
        holdq = DiscardValue(held_d=self.h2.hold([True] + [False] * 4))
        h2d4r = holdq._draw_for_ranks(gsize=3, cnt_held_only=False)
        self.assertEqual(h2d4r, 4102)

        h3d4r = DiscardValue(held_d=self.h3.hold([False] * 3 + [True] * 2))
        self.assertEqual(h3d4r._draw_for_ranks(gsize=3), 1893)

    def test_pair_jqka(self):
        holdq = DiscardValue(held_d=self.h2.hold([True] + [False] * 4))
        self.assertEqual(holdq.pair_jqka(), 45456)

        holdaa = DiscardValue(held_d=self.h3.hold([False] * 3 + [True] * 2))
        self.assertEqual(holdaa.pair_jqka(), 11559)

        twop = DiscardValue(
            held_d=HandAnalyzer("acad8h8s2c").hold([True] * 2 + [False] * 3)
        )
        self.assertEqual(twop.pair_jqka(), 11520)

        nohi = DiscardValue(held_d=HandAnalyzer("td9c8d5c2c").hold([False] * 5))
        self.assertEqual(nohi.pair_jqka(), 241680)

        lowp = DiscardValue(
            held_d=HandAnalyzer("qcjckdtdth").hold([True] * 4 + [False])
        )
        self.assertEqual(lowp.pair_jqka(), 9)

        threek = DiscardValue(held_d=HandAnalyzer("4h4c5h3h4s").hold([True] * 5))
        self.assertEqual(threek.pair_jqka(), 0)

    def test_four_kind(self):
        holdaa = DiscardValue(held_d=self.h3.hold([False] * 3 + [True] * 2))
        self.assertEqual(holdaa.four_kind(), 45)

        holdq = DiscardValue(held_d=self.h2.hold([True] + [False] * 4))
        self.assertEqual(holdq.four_kind(), 52)

        h3hold8aa = DiscardValue(held_d=self.h3.hold([False] * 2 + [True] * 3))
        self.assertEqual(h3hold8aa.four_kind(), 1)

        discard_h2 = DiscardValue(held_d=self.h2.hold([False] * 5))
        self.assertEqual(discard_h2.four_kind(), 344)

        fh = DiscardValue(
            held_d=HandAnalyzer("qdqcqh2s2d").hold([True] * 3 + [False] * 2)
        )
        self.assertEqual(fh.four_kind(), 46)

        fourk = DiscardValue(
            held_d=HandAnalyzer("qcqdqhqs2c").hold([True] * 4 + [False])
        )
        self.assertEqual(fourk.four_kind(), 47)

        h2A8 = HandAnalyzer("".join(self.h2.hand), payouts=self.aces8s_d)
        h2A8holdq = DiscardValue(held_d=h2A8.hold([True] + [False] * 4))
        h2A8holdq8 = DiscardValue(held_d=h2A8.hold([True, False, True] + [False] * 2))
        spec = ["A", "7", "8"]
        self.assertEqual(h2A8holdq.four_kind(specials=spec), 50)
        self.assertEqual(h2A8holdq8.four_kind(specials=spec), 1)

        junk6 = HandAnalyzer("tc9d6h5s2c", payouts=self.aces8s_d)
        j6disc = DiscardValue(held_d=junk6.hold([False] * 5))
        self.assertEqual(j6disc.four_kind(specials=spec), 215)

        h2tbp = HandAnalyzer("".join(self.h2.hand), payouts=self.tripbonusplus_d)
        h2tbpholdq = DiscardValue(held_d=h2tbp.hold([True] + [False] * 4))
        h2tbpholdq8 = DiscardValue(held_d=h2tbp.hold([True, False, True] + [False] * 2))
        spec_tbp = "A234"
        self.assertEqual(h2tbpholdq.four_kind(specials=spec_tbp), 49)
        self.assertEqual(h2tbpholdq8.four_kind(specials=spec_tbp), 2)

        junk6tbp = HandAnalyzer("tc9d6h5s2c", payouts=self.tripbonusplus_d)
        j6disctbp = DiscardValue(held_d=junk6tbp.hold([False] * 5))
        self.assertEqual(j6disctbp.four_kind(specials=spec_tbp), 215)

    def test_two_pair(self):
        twop = HandAnalyzer("acad8h8s2c")
        twopdv1 = DiscardValue(held_d=twop.hold([True] * 4 + [False]))
        twopdv2 = DiscardValue(held_d=twop.hold([True] * 5))
        twopdv3 = DiscardValue(held_d=twop.hold([True] * 3 + [False] * 2))
        self.assertEqual(twopdv1.two_pair(), 43)
        self.assertEqual(twopdv2.two_pair(), 1)
        self.assertEqual(twopdv3.two_pair(), 149)

        discard_h2 = DiscardValue(held_d=self.h2.hold([False] * 5))
        self.assertEqual(discard_h2.two_pair(), 71802)

        holdq = DiscardValue(held_d=self.h2.hold([True] + [False] * 4))
        self.assertEqual(holdq.two_pair(), 8874)

        holdq9 = DiscardValue(held_d=self.h2.hold([True] * 2 + [False] * 3))
        self.assertEqual(holdq9.two_pair(), 711)

        holdq98 = DiscardValue(held_d=self.h2.hold([True] * 3 + [False] * 2))
        self.assertEqual(holdq98.two_pair(), 27)

        hold98a = DiscardValue(held_d=self.h3.hold([False, True, True, True, False]))
        self.assertEqual(hold98a.two_pair(), 21)

        holdq985 = DiscardValue(held_d=self.h2.hold([True] * 4 + [False] * 1))
        self.assertEqual(holdq985.two_pair(), 0)

        h3hold8aa = DiscardValue(held_d=self.h3.hold([False] * 2 + [True] * 3))
        self.assertEqual(h3hold8aa.two_pair(), 186)

        holdaa = DiscardValue(held_d=self.h3.hold([False] * 3 + [True] * 2))
        self.assertEqual(holdaa.two_pair(), 2592)

        discaa = DiscardValue(held_d=self.h3.hold([True] * 3 + [False] * 2))
        self.assertEqual(discaa.two_pair(), 27)

        fourk = DiscardValue(
            held_d=HandAnalyzer("qcqdqhqs2c").hold([True] * 4 + [False])
        )
        self.assertEqual(fourk.two_pair(), 0)

        fh = DiscardValue(held_d=HandAnalyzer("qdqcqh2s2d").hold([True] * 5))
        self.assertEqual(fh.two_pair(), 0)

    def test_full_house(self):
        discard_h2 = DiscardValue(held_d=self.h2.hold([False] * 5))
        self.assertEqual(discard_h2.full_house(), 2124)

        holdq = DiscardValue(held_d=self.h2.hold([True] + [False] * 4))
        self.assertEqual(holdq.full_house(), 288)

        holdq9 = DiscardValue(held_d=self.h2.hold([True] * 2 + [False] * 3))
        self.assertEqual(holdq9.full_house(), 18)

        holdq98 = DiscardValue(held_d=self.h2.hold([True] * 3 + [False] * 2))
        self.assertEqual(holdq98.full_house(), 0)

        holdaa = DiscardValue(held_d=self.h3.hold([False] * 3 + [True] * 2))
        self.assertEqual(holdaa.full_house(), 165)

        h3hold8aa = DiscardValue(held_d=self.h3.hold([False] * 2 + [True] * 3))
        self.assertEqual(h3hold8aa.full_house(), 9)

        trips = HandAnalyzer("qcqdqh7c2d")
        tripsonly = DiscardValue(held_d=trips.hold([True] * 3 + [False] * 2))
        self.assertEqual(tripsonly.full_house(), 66)
        tripsp1 = DiscardValue(held_d=trips.hold([True] * 4 + [False]))
        self.assertEqual(tripsp1.full_house(), 3)

        twop = DiscardValue(
            held_d=HandAnalyzer("acad8h8s2c").hold([True] * 4 + [False])
        )
        self.assertEqual(twop.full_house(), 4)

        fh1 = DiscardValue(held_d=HandAnalyzer("qdqcqh2s2d").hold([True] * 5))
        self.assertEqual(fh1.full_house(), 1)

        fh2 = DiscardValue(held_d=HandAnalyzer("qdqcqh2s2d").hold([True] * 4 + [False]))
        self.assertEqual(fh2.full_house(), 2)

    def test_straight(self):
        discard_h2 = DiscardValue(held_d=self.h2.hold([False] * 5))
        self.assertEqual(discard_h2.straight(), 5832)

        holdq = DiscardValue(held_d=self.h2.hold([True] + [False] * 4))
        self.assertEqual(holdq.straight(), 590)

        holdq9 = DiscardValue(held_d=self.h2.hold([True] * 2 + [False] * 3))
        self.assertEqual(holdq9.straight(), 112)

        holdq98 = DiscardValue(held_d=self.h2.hold([True] * 3 + [False] * 2))
        self.assertEqual(holdq98.straight(), 16)

    def test_straight_flush(self):
        discard_h2 = DiscardValue(held_d=self.h2.hold([False] * 5))
        self.assertEqual(discard_h2.straight_flush(), 21)

        holdq = DiscardValue(held_d=self.h2.hold([True] + [False] * 4))
        self.assertEqual(holdq.straight_flush(), 1)

        h1aj = DiscardValue(held_d=self.h1.hold([True] * 2 + [False] * 3))
        self.assertEqual(h1aj.straight_flush(), 0)

        junkd = DiscardValue(held_d=self.junk.hold([False] * 5))
        self.assertEqual(junkd.straight_flush(), 16)
        junkt = DiscardValue(held_d=self.junk.hold([True] + [False] * 4))
        self.assertEqual(junkt.straight_flush(), 4)
        junk8 = DiscardValue(held_d=self.junk.hold([False, False, True, False, False]))
        self.assertEqual(junk8.straight_flush(), 5)

    def test_flush(self):
        holdq = DiscardValue(held_d=self.h2.hold([True] + [False] * 4))
        self.assertEqual(holdq.flush(), 328)

        holdq9 = DiscardValue(held_d=self.h2.hold([True] * 2 + [False] * 3))
        self.assertEqual(holdq9.flush(), 0)

        holdq8 = DiscardValue(held_d=self.h2.hold([True, False, True, False, False]))
        self.assertEqual(holdq8.flush(), 164)

        junkd = DiscardValue(held_d=self.junk.hold([False] * 5))
        self.assertEqual(junkd.flush(), 2819)
        junkt = DiscardValue(held_d=self.junk.hold([True] + [False] * 4))
        self.assertEqual(junkt.flush(), 490)

    def test_four_kindA8(self):
        h2A8 = HandAnalyzer("".join(self.h2.hand), payouts=self.aces8s_d)
        h2A8dv = DiscardValue(held_d=h2A8.hold([True] + [False] * 4))
        self.assertEqual(h2A8dv.four_kindA8(), 1)

        junk6 = HandAnalyzer("tc9d6h5s2c", payouts=self.aces8s_d)
        junk6dv = DiscardValue(held_d=junk6.hold([False] * 5))
        self.assertEqual(junk6dv.four_kindA8(), 86)

        aaa = HandAnalyzer("ACADAH9CQH", payouts=self.aces8s_d)
        aaadv = DiscardValue(held_d=aaa.hold([True] * 3 + [False] * 2))
        self.assertEqual(aaadv.four_kindA8(), 46)

    def test_four_kind7(self):
        h2A8 = HandAnalyzer("".join(self.h2.hand), payouts=self.aces8s_d)
        h2A8dv = DiscardValue(held_d=h2A8.hold([True] + [False] * 4))
        self.assertEqual(h2A8dv.four_kind7(), 1)
        h2A8dv2 = DiscardValue(held_d=h2A8.hold([True, False, True] + [False] * 2))
        self.assertEqual(h2A8dv2.four_kind7(), 0)

        junk6 = HandAnalyzer("tc9d6h5s2c", payouts=self.aces8s_d)
        junk6dv = DiscardValue(held_d=junk6.hold([False] * 5))
        self.assertEqual(junk6dv.four_kind7(), 43)

    def test_four_kindA(self):
        h2tbp = HandAnalyzer("".join(self.h2.hand), payouts=self.tripbonusplus_d)
        h2tbpdv = DiscardValue(held_d=h2tbp.hold([True] + [False] * 4))
        self.assertEqual(h2tbpdv.four_kindA(), 1)
        h2tbpdv2 = DiscardValue(held_d=h2tbp.hold([True, False, True] + [False] * 2))
        self.assertEqual(h2tbpdv2.four_kindA(), 0)

        junk6 = HandAnalyzer("tc9d6h5s2c", payouts=self.tripbonusplus_d)
        junk6dv = DiscardValue(held_d=junk6.hold([False] * 5))
        self.assertEqual(junk6dv.four_kindA(), 43)

    def test_four_kind234(self):
        h2tbp = HandAnalyzer("".join(self.h2.hand), payouts=self.tripbonusplus_d)
        h2tbpdv = DiscardValue(held_d=h2tbp.hold([True] + [False] * 4))
        self.assertEqual(h2tbpdv.four_kind234(), 2)
        h2tbpdv2 = DiscardValue(held_d=h2tbp.hold([True, False, True] + [False] * 2))
        self.assertEqual(h2tbpdv2.four_kind234(), 0)

        junk6 = HandAnalyzer("tc9d6h5s2c", payouts=self.tripbonusplus_d)
        junk6dv = DiscardValue(held_d=junk6.hold([False] * 5))
        self.assertEqual(junk6dv.four_kind234(), 86)
