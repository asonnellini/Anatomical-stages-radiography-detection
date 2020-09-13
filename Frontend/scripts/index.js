var backendip = 'IP of your Server'

function take_snapshot() {
    // take snapshot and get image data
    Webcam.snap(
        function(data_uri) {
            // display results in page
            $('#image').html('<img src="'+data_uri+'"/>');
            $.post(
                'http://'+backendip+':5000/get_picture'+'/',
                data_uri,
                result_f,
                'html'
            );
            function result_f(data_back){
                $('#results').html($.parseHTML(data_back));
            }
        }
    );
}

function goDeepToTheBones() {

    var pic = $('#image').contents().length

    if(pic>0 ){
        $.post(
            'http://'+backendip+':5000/compare/',
            "nothing",
            result_f,
            'html'
        );
        function result_f(data_back){
            $('#compare').html($.parseHTML(data_back));
        }
    }
}
