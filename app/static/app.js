let get_health_flags = function() {
    health_flags = $('.health:checkbox:checked')
    .map(function(){
    return $(this).val();
    }).get();
    return health_flags
}

let get_label_input = function() {
    let label_in = $("input#label_in").val()
    health_flags = get_health_flags()
    return {"label_in": label_in,
            "health_flags": health_flags}
}

let get_url_input = function() {
    let url_in = $("input#url_in").val()
    health_flags = get_health_flags()
    return {"url_in": url_in,
            "health_flags": health_flags}
}

let send_label_input = function(label_input) {
    $.ajax({
        url: '/result_label',
        contentType: "application/json; charset=utf-8",
        type: 'POST',
        success: function (report) {
            display_report(report);
        },
        data: JSON.stringify(label_input)
    });
};

let send_url_input = function(url_input) {
    $.ajax({
        url: '/result_url',
        contentType: "application/json; charset=utf-8",
        type: 'POST',
        success: function (report) {
            display_report(report);
        },
        data: JSON.stringify(url_input)
    });
};

let display_report = function(report) {
    document.getElementById("report").style.display = 'block';
    $("span#group_size").html(report.group_size)
    $("p#group_desc").html(report.group_desc)
    $("span#recp_label").html(report.recp_label)
    $("a#recp_url").attr("href", report.recp_url)
    $("p#recp_text").html(report.recp_text)
    $("p#recp_stats").html(report.recp_stats)
};

$(document).ready(function() {
    $("button#submit_label").click(function() {
        let label_input = get_label_input()
        send_label_input(label_input)
    })
    $("button#submit_url").click(function() {
        let url_input = get_url_input()
        send_url_input(url_input)
    })
})
