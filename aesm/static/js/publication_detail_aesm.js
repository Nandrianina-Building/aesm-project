function getCookie(name){

    return document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='))
        ?.split('=')[1]

}

const csrftoken = getCookie('csrftoken')


document.querySelectorAll('.like-btn').forEach(button => {

    button.addEventListener('click', function () {

        const pubId = this.dataset.id
        const url = this.dataset.url

        const icon = this.querySelector('i')
        const text = this.querySelector('.like-text')

        fetch(url, {

            method: 'POST',

            headers: {
                'X-CSRFToken': csrftoken
            }

        })

        .then(response => response.json())

        .then(data => {

            document.getElementById(`count-${pubId}`).textContent =
                data.likes_count

            if(data.liked){

                icon.classList.remove('fa-regular')

                icon.classList.add('fa-solid')
                icon.classList.add('liked')

                text.textContent = "J'aime deja"

            } else {

                icon.classList.remove('fa-solid')
                icon.classList.remove('liked')

                icon.classList.add('fa-regular')

                text.textContent = "J'aime"

            }

        })

    })

})