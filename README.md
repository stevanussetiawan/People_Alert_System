<h1>People Alert System</h1>

<p>This project is a <strong>People Alert System</strong> that utilizes a YOLOv8 model to detect and monitor the number of people in a specified area using a webcam or video feed. The system raises an alert if more than a specified number of people are visible continuously for a certain period of time.</p>

<h2>Features</h2>
<ul>
    <li>Real-time detection using YOLOv8.</li>
    <li>Configurable input source: webcam or video files.</li>
    <li>Adjustable alert threshold for the number of people.</li>
    <li>Option to specify output directory to save processed frames.</li>
</ul>

<h2>Prerequisites</h2>
<ul>
    <li>Python 3.8+</li>
    <li>Required libraries:
        <ul>
            <li>torch</li>
            <li>opencv-python</li>
            <li>ultralytics (for YOLOv8)</li>
            <li>numpy</li>
        </ul>
    </li>
</ul>
<p>Install the required libraries using:</p>
<pre><code>pip install torch opencv
