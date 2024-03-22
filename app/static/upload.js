// upload.js
document.getElementById('uploadForm').addEventListener('submit', function() {
    var progressBar = document.getElementById('progressBar');
    progressBar.style.display = 'block';

    var xhr = new XMLHttpRequest();
    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            var percentComplete = (e.loaded / e.total) * 100;
            progressBar.querySelector('.progress-bar').style.width = percentComplete + '%';
        }
    };

    xhr.open('POST', '{{ url_for('video.upload') }}', true);
    xhr.send(new FormData(this));
});
