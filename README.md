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
<p>Install the required libraries using:</p>
<pre><code>ppip install -r requirements.txt</code></pre>

<h2>Getting Started</h2>
<ol>
    <li>Clone the repository:
        <pre><code>git clone https://github.com/stevanussetiawan/people-alert-system.git
cd people-alert-system</code></pre>
    </li>
    <li>Download the YOLOv8 model weights and save them in the <code>models</code> directory:
        <pre><code>mkdir models
# Place yolov8n.pt or your custom model in the models directory.</code></pre>
    </li>
    <li>Run the system:
        <pre><code>python main.py --path webcam --weight_path models/yolov8n.pt --output_dir output_frames --n_people 1</code></pre>
    </li>
</ol>

<h2>Arguments</h2>
<ul>
    <li><code>--path</code>: Path to the input source (e.g., <code>webcam</code> for webcam input or <code>path/to/video.mp4</code> for video files).</li>
    <li><code>--weight_path</code>: Path to the YOLO model weights (e.g., <code>models/yolov8n.pt</code>).</li>
    <li><code>--output_dir</code>: Directory where output frames and results will be saved.</li>
    <li><code>--n_people</code>: Number of people to observe before triggering an alert.</li>
</ul>

<h2>Example</h2>
<p>Run the following command to use the webcam as input and monitor for at least 1 person:</p>
<pre><code>python main.py --path webcam --weight_path models/yolov8n.pt --output_dir output_frames --n_people 1</code></pre>

<h2>Output</h2>
<ul>
    <li>Detected frames will be saved in the specified <code>output_dir</code>.</li>
    <li>Alerts will be logged in the console.</li>
</ul>

<h2>License</h2>
<p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>

<h2>Contributing</h2>
<p>Contributions are welcome! Please fork the repository and submit a pull request for any improvements.</p>

<h2>Acknowledgements</h2>
<ul>
    <li><a href="https://github.com/ultralytics">Ultralytics</a> for the YOLOv8 model.</li>
    <li><a href="https://opencv.org/">OpenCV</a> for image processing.</li>
</ul>
