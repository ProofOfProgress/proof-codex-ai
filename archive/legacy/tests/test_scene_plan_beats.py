from shorts_bot.production.scene_plan import Pose, plan_scene


def test_beat_hint_bathroom_pose():
    plan = plan_scene("some line", beat_hint="figure huddled in bathroom stall")
    assert plan.pose == Pose.HUDDLED


def test_office_bathroom_keywords():
    plan = plan_scene("I hide in the office bathroom stall")
    assert plan.pose == Pose.HUDDLED
    assert plan.prop == "stall"


def test_cosy_couch_overwhelm():
    plan = plan_scene("I can't move from the couch under my blanket")
    assert plan.pose == Pose.HUDDLED
    assert plan.prop == "blanket"
