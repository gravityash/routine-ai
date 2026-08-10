import os

replacements_dashboard = {
    '<h1>Welcome, {{ session.get(\'username\') }} ✨</h1>': '<h1 style="display:inline" data-i18n="dash_title">Welcome, </h1><h1 style="display:inline"> {{ session.get(\'username\') }} ✨</h1>',
    '<p>Your personalized AI lifestyle dashboard</p>': '<p data-i18n="dash_desc">Your personalized AI lifestyle dashboard</p>',
    '<h3><span style="font-size:1.2em">📋</span> Enter Your Daily Data</h3>': '<h3><span style="font-size:1.2em">📋</span> <span data-i18n="dash_enter_data">Enter Your Daily Data</span></h3>',
    '<label>Age (years)</label>': '<label data-i18n="lbl_age">Age (years)</label>',
    '<label>Weight (kg)</label>': '<label data-i18n="lbl_weight">Weight (kg)</label>',
    '<label>Sleep Hours</label>': '<label data-i18n="lbl_sleep">Sleep Hours</label>',
    '<label>Stress Level (1-10)</label>': '<label data-i18n="lbl_stress">Stress Level (1-10)</label>',
    '<label>Steps Walked</label>': '<label data-i18n="lbl_steps">Steps Walked</label>',
    '<label>Water Intake (liters)</label>': '<label data-i18n="lbl_water">Water Intake (liters)</label>',
    '<label>Screen Time (hours)</label>': '<label data-i18n="lbl_screen">Screen Time (hours)</label>',
    '<label>Work Hours</label>': '<label data-i18n="lbl_work">Work Hours</label>',
    '<label>Protein Intake (grams)</label>': '<label data-i18n="lbl_protein">Protein Intake (grams)</label>',
    '<label>Calories Intake (kcal)</label>': '<label data-i18n="lbl_calories">Calories Intake (kcal)</label>',
    '<label>Exercise Minutes</label>': '<label data-i18n="lbl_exercise">Exercise Minutes</label>',
    '<label>Meditation Minutes</label>': '<label data-i18n="lbl_meditation">Meditation Minutes</label>',
    '<label>Gender</label>': '<label data-i18n="lbl_gender">Gender</label>',
    '<label>Fitness Goal</label>': '<label data-i18n="lbl_goal">Fitness Goal</label>',
    '<option value="Male">Male</option>': '<option value="Male" data-i18n="opt_male">Male</option>',
    '<option value="Female">Female</option>': '<option value="Female" data-i18n="opt_female">Female</option>',
    '<option value="weight_loss">Weight Loss</option>': '<option value="weight_loss" data-i18n="opt_weight">Weight Loss</option>',
    '<option value="muscle_gain">Muscle Gain</option>': '<option value="muscle_gain" data-i18n="opt_muscle">Muscle Gain</option>',
    '<span id="btnText">✨ Generate AI Plan</span>': '<span id="btnText" data-i18n="btn_generate">✨ Generate AI Plan</span>',
    '<h3><span style="font-size:1.2em">📈</span> Health Metrics</h3>': '<h3><span style="font-size:1.2em">📈</span> <span data-i18n="dash_metrics">Health Metrics</span></h3>',
}

replacements_home = {
    '<a href="/">Home</a>': '<a href="/" data-i18n="nav_home">Home</a>',
    '<a href="/about">About Us</a>': '<a href="/about" data-i18n="nav_about">About Us</a>',
    '<a href="/login">Login</a>': '<a href="/login" data-i18n="nav_login">Login</a>',
    '<a href="/register" class="btn" style="padding: 8px 20px;">Sign Up</a>': '<a href="/register" class="btn" style="padding: 8px 20px;" data-i18n="nav_signup">Sign Up</a>',
    '<h1 class="gradient-text">Discover the Root Cause of Your Health Patterns</h1>': '<h1 class="gradient-text" data-i18n="hero_title">Discover the Root Cause of Your Health Patterns</h1>',
    '<p>We analyze your daily lifestyle, sleep, and stress using advanced Machine Learning to provide clinical-grade, personalized health optimization plans.</p>': '<p data-i18n="hero_desc">We analyze your daily lifestyle, sleep, and stress using advanced Machine Learning to provide clinical-grade, personalized health optimization plans.</p>',
    '<a href="/register" class="btn">Get Started Free</a>': '<a href="/register" class="btn" data-i18n="btn_start_free">Get Started Free</a>',
    '<a href="/about" class="btn btn-outline">Learn More</a>': '<a href="/about" class="btn btn-outline" data-i18n="btn_learn_more">Learn More</a>',
    '<h2>Why Choose <span class="gradient-text">WellnessIQ?</span></h2>': '<h2><span data-i18n="feat_title">Why Choose </span><span class="gradient-text">WellnessIQ?</span></h2>',
    '<h3>Root Cause Analysis</h3>': '<h3 data-i18n="feat_1_title">Root Cause Analysis</h3>',
    '<p>Our ML engine analyzes your habits to find the exact triggers for poor sleep, stress, or fatigue.</p>': '<p data-i18n="feat_1_desc">Our ML engine analyzes your habits to find the exact triggers for poor sleep, stress, or fatigue.</p>',
    '<h3>Holistic Approach</h3>': '<h3 data-i18n="feat_2_title">Holistic Approach</h3>',
    '<p>We bridge the gap between diet, exercise, and mental well-being for a complete transformation.</p>': '<p data-i18n="feat_2_desc">We bridge the gap between diet, exercise, and mental well-being for a complete transformation.</p>',
    '<h3>Explainable AI</h3>': '<h3 data-i18n="feat_3_title">Explainable AI</h3>',
    '<p>No generic advice. Every recommendation is tailored, concise, and clinically grounded in your data.</p>': '<p data-i18n="feat_3_desc">No generic advice. Every recommendation is tailored, concise, and clinically grounded in your data.</p>',
    '<h3>Progress Tracking</h3>': '<h3 data-i18n="feat_4_title">Progress Tracking</h3>',
    '<p>Watch your health metrics improve with our dynamic, interactive dashboard over time.</p>': '<p data-i18n="feat_4_desc">Watch your health metrics improve with our dynamic, interactive dashboard over time.</p>',
    '<h2>How It <span class="gradient-text">Works</span></h2>': '<h2><span data-i18n="how_title">How It </span><span class="gradient-text">Works</span></h2>',
    '<h3>Share Your Daily Metrics</h3>': '<h3 data-i18n="step_1_title">Share Your Daily Metrics</h3>',
    '<p>Input your sleep, steps, stress levels, and diet into our secure dashboard.</p>': '<p data-i18n="step_1_desc">Input your sleep, steps, stress levels, and diet into our secure dashboard.</p>',
    '<h3>Advanced ML Analysis</h3>': '<h3 data-i18n="step_2_title">Advanced ML Analysis</h3>',
    '<p>Our trained HistGradientBoostingClassifier evaluates your metrics against thousands of baseline models.</p>': '<p data-i18n="step_2_desc">Our trained HistGradientBoostingClassifier evaluates your metrics against thousands of baseline models.</p>',
    '<h3>Get Your Protocol</h3>': '<h3 data-i18n="step_3_title">Get Your Protocol</h3>',
    '<p>Our Generative AI translates the ML baseline into an easy-to-follow, highly actionable daily plan.</p>': '<p data-i18n="step_3_desc">Our Generative AI translates the ML baseline into an easy-to-follow, highly actionable daily plan.</p>',
    '<h2>Meet the <span class="gradient-text">Team</span></h2>': '<h2><span data-i18n="team_title">Meet the </span><span class="gradient-text">Team</span></h2>',
    '<h2>Ready to Transform Your Health?</h2>': '<h2 data-i18n="cta_title">Ready to Transform Your Health?</h2>',
    '<a href="/register" class="btn" style="font-size:1.3rem; padding:15px 40px;">Start Free Analysis</a>': '<a href="/register" class="btn" style="font-size:1.3rem; padding:15px 40px;" data-i18n="btn_start_analysis">Start Free Analysis</a>',
    '<p>Empowering you to take control of your health through data-driven AI insights.</p>': '<p data-i18n="footer_desc">Empowering you to take control of your health through data-driven AI insights.</p>',
    '<h4>Quick Links</h4>': '<h4 data-i18n="footer_links">Quick Links</h4>',
    '<h4>Contact</h4>': '<h4 data-i18n="footer_contact">Contact</h4>',
}

def process_file(file, replacements):
    with open(f'templates/{file}', 'r', encoding='utf-8') as f:
        content = f.read()
    for k, v in replacements.items():
        content = content.replace(k, v)
    with open(f'templates/{file}', 'w', encoding='utf-8') as f:
        f.write(content)

process_file('dashboard.html', replacements_dashboard)
process_file('home.html', replacements_home)

# Now update the run() and API requests to include language
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

run_payload = """const data={
age:+age.value,
gender:gender.value,
weight:+weight.value,
height:175,
bmi:22.9,
goal:goal.value,
sleep_hours:+sleep.value,
sleep_quality:2,
bedtime_hour:1,
wake_time:7,
fatigue_level:8,
steps_walked:+steps.value,
exercise_minutes:+exercise.value,
exercise_type:"none",
calories_burned:150,
heart_rate_avg:85,
calories_intake:+calories.value,
protein_intake:+protein.value,
junk_food_freq:5,
water_intake:+water.value,
meal_frequency:3,
stress_level:+stress.value,
mood:4,
screen_time:+screen_time.value,
work_hours:+work_hours.value,
social_interaction:"low",
meditation_minutes:+meditation.value,
hair_condition:2,
skin_condition:2,
sun_exposure:4,
water_quality:"average",
language: localStorage.getItem('language') || 'en'
};

const historyStr = localStorage.getItem('healthHistory');
let healthHistory = historyStr ? JSON.parse(historyStr) : [];
data.timestamp = new Date().toISOString();
healthHistory.push(data);
localStorage.setItem('healthHistory', JSON.stringify(healthHistory));
localStorage.setItem('userData', JSON.stringify(data));
"""

dash = dash.replace("""const data={
age:+age.value,
gender:gender.value,
weight:+weight.value,
height:175,
bmi:22.9,
goal:goal.value,
sleep_hours:+sleep.value,
sleep_quality:2,
bedtime_hour:1,
wake_time:7,
fatigue_level:8,
steps_walked:+steps.value,
exercise_minutes:+exercise.value,
exercise_type:"none",
calories_burned:150,
heart_rate_avg:85,
calories_intake:+calories.value,
protein_intake:+protein.value,
junk_food_freq:5,
water_intake:+water.value,
meal_frequency:3,
stress_level:+stress.value,
mood:4,
screen_time:+screen_time.value,
work_hours:+work_hours.value,
social_interaction:"low",
meditation_minutes:+meditation.value,
hair_condition:2,
skin_condition:2,
sun_exposure:4,
water_quality:"average"
};

localStorage.setItem('userData', JSON.stringify(data));""", run_payload)

# Add Progress Dashboard Button
prog_btn = """<div class="card" style="text-align:center; padding:20px; margin-top:20px;">
    <a href="/progress" class="btn" style="width:100%; box-sizing:border-box; background:linear-gradient(135deg, #8b5cf6, #3b82f6);"><span data-i18n="btn_progress">📊 View Progress Dashboard</span></a>
</div>"""
dash = dash.replace('<!-- CHARTS -->', prog_btn + '\\n<!-- CHARTS -->')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash)

print("Updated dashboard logic and added data-i18n tags.")
