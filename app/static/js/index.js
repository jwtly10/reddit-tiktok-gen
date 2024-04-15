document.addEventListener('DOMContentLoaded', function() {
    const post_title = document.getElementById('post_title');
    const post_content = document.getElementById('post_content');
    const background_video = document.getElementById('background_video');
    const generate_btn = document.getElementById('generate-btn');

    // Load data from local storage on load
    post_title.value = localStorage.getItem('post_title');
    post_content.value = localStorage.getItem('post_content');
    if (localStorage.getItem('background_video') === null) {
        background_video.value = 'Select a base background video';
    } else {
        background_video.value = localStorage.getItem('background_video');
    }

    // Save data to local storage on change
    post_title.addEventListener('input', function() {
        localStorage.setItem('post_title', post_title.value);
    })

    post_content.addEventListener('input', function() {
        localStorage.setItem('post_content', post_content.value);
    })

    background_video.addEventListener('change', function() {
        localStorage.setItem('background_video', background_video.value);
    })
})
