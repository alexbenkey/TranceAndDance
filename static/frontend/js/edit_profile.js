const editProfileModalElement = document.getElementById("editProfileModal");
const editProfileModal =  new bootstrap.Modal(editProfileModalElement);

const saveChangesBtn = document.getElementById("saveChanges");

if (saveChangesBtn) {
    saveChangesBtn.addEventListener("click", async function(event) {
        try {
            event.preventDefault();
            const newUsername = document.getElementById("newUsername").value;
            const newMail = document.getElementById("newMail").value;
            const newAvatar = document.getElementById("newAvatar").files[0];
            const preferredLanguage = document.getElementById("preferredLanguage").value;

            console.log("New Username:", newUsername);
            console.log("New Email:", newMail);
            console.log("New Pref Language:", preferredLanguage);

            const formData = new FormData();

            if (newUsername) 
                formData.append("newUsername", newUsername);
            if (newMail)
                formData.append("newMail", newMail);
            if (newAvatar) 
                formData.append("newAvatar", newAvatar);
            if (preferredLanguage)
                formData.append("preferred_language", preferredLanguage);

            console.log("form data: ", formData);
            const response = await fetch(`/data/api/editProfile/`, {
                method: "POST",
                credentials: "include",
                headers: {
                },
                body: formData
            });

            if (!response.ok) {
                const responseError = await response.json();
                if (response.status == 400 && responseError)
                    alert(`${responseError.error}. Please try again!`);
                throw new Error(`error, status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Edit Data:", data);

            if (newUsername) {
                document.getElementById("username").textContent = data.username;
            }
            if(newMail){
                document.getElementById("userEmail").textContent = data.email;
            }
            if (data.avatar_url) {
                document.getElementById("userAvatar").src = data.avatar_url; // Assuming API returns the new image URL
            }
            if (preferredLanguage) {
                await fetch("/i18n/setlang/", {
                    method: "POST",
                    credentials: 'include',
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: `language=${preferredLanguage}&next=/`
                });
                location.reload(); // Now reload in the new language
            }
            editProfileModal.hide();
            profileModal.show();
            loadProfile("self");

        } catch (error) {
            console.error("Error updating profile:", error);
        }
    });
}

const editCloseBtn = document.getElementById("editCloseBtn")
if(editCloseBtn){
    editCloseBtn.addEventListener("click", function (){
        console.log("profile close clicked");
        history.back();
    });
}
