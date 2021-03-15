function getDetail(url) {
    new_url = url.replace("http://", "//")
    document.getElementById("detail-display1").src = new_url;
    document.getElementById("detail-display2").src = new_url;
}

function firstButton() {
    document.getElementById("first-semester").style.display = "block"
    document.getElementById("second-semester").style.display = "none"
    document.getElementById("top").style.backgroundColor = "#cdffcd"
    document.getElementById("top2").style.backgroundColor = "#ffffff"
}

function secondButton() {
    document.getElementById("first-semester").style.display = "none"
    document.getElementById("second-semester").style.display = "block"
    document.getElementById("top").style.backgroundColor = "#ffffff"
    document.getElementById("top2").style.backgroundColor = "#cdffcd"
}

window.onload = function() {
    console.log(location.hash)
    if (location.hash == "#top2") {
        secondButton()  
    } else {
        firstButton()
    }
}
