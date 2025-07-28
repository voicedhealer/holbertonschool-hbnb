document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------------
    // OUTIL : lire un cookie par son nom
    // -----------------------------------------
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    // Récupération du JWT une seule fois au début
    const jwt = getCookie('jwt');

    // -----------------------------------------
    // Gestion bouton Connexion / Déconnexion
    // -----------------------------------------
    const loginBtn = document.querySelector('.login-button');
    if (loginBtn) {
        const newLoginBtn = loginBtn.cloneNode(true);
        loginBtn.parentNode.replaceChild(newLoginBtn, loginBtn);

        if (jwt) {
            newLoginBtn.textContent = "Déconnexion";
            newLoginBtn.href = "#";
            newLoginBtn.addEventListener('click', (e) => {
                e.preventDefault();
                // Supprime cookie JWT (expire dans le passé)
                document.cookie = "jwt=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax";
                window.location.replace('index.html');
            });
        } else {
            newLoginBtn.textContent = "Connexion";
            newLoginBtn.href = "login.html";
        }
    }

    // -----------------------------------------
    // PAGE LOGIN : gestion formulaire connexion + erreurs
    // -----------------------------------------
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const payload = { email, password };

            try {
                const response = await fetch('http://localhost:5001/api/v1/auth/login', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.access_token) {
                        // Stockage cookie JWT
                        document.cookie = `jwt=${data.access_token}; path=/; SameSite=Lax`;
                        // Redirection vers la page d'accueil
                        window.location.replace('index.html');
                    } else {
                        throw new Error("Le serveur n'a pas retourné de token.");
                    }
                } else {
                    let msg = 'Identifiants invalides';
                    try {
                        const err = await response.json();
                        if (err.message) msg = err.message;
                    } catch (_) { }
                    throw new Error(msg);
                }
            } catch (error) {
                if (loginError) {
                    loginError.textContent = error.message || "Erreur de connexion";
                    loginError.style.display = 'block';
                } else {
                    alert(error.message || "Erreur de connexion");
                }
            }
        });
    }

    // -----------------------------------------
    // PAGE ACCUEIL (index.html) : affichage lieux + filtrage par prix
    // -----------------------------------------
    const placesList = document.getElementById('places-list');
    const priceFilter = document.getElementById('price-filter');
    if (placesList && priceFilter) {
        const options = jwt ? { 
            headers: { 'Authorization': 'Bearer ' + jwt },
            credentials: 'include'
        } : {};

        fetch('http://localhost:5001/api/v1/places/', options)
            .then(resp => {
                if (!resp.ok) throw new Error(`Erreur API (${resp.status}): ${resp.statusText}`);
                return resp.json();
            })
            .then(places => {
                placesList.innerHTML = '';

                places.forEach(place => {
                    const card = document.createElement('div');
                    card.className = 'place-card';
                    card.dataset.price = place.price_by_night;
                    card.innerHTML = `
                        <h3 class="place-name">${place.name}</h3>
                        <p class="place-price">${place.price_by_night} €/nuit</p>
                        <button class="details-button" onclick="window.location.href='place.html?id=${place.id}'">
                          Voir les détails
                        </button>
                    `;
                    placesList.appendChild(card);
                });

                // Génération options filtres prix (prix uniques triés)
                const uniqPrices = Array.from(new Set(places.map(p => p.price_by_night))).sort((a, b) => a - b);
                priceFilter.innerHTML = `<option value="">Tous</option>` +
                    uniqPrices.map(prix => `<option value="${prix}">≤ ${prix} €</option>`).join('');

                // Événement filtrage des lieux par prix via style.display
                priceFilter.addEventListener('change', () => {
                    const max = Number(priceFilter.value);
                    const cards = placesList.querySelectorAll('.place-card');
                    let nbVisible = 0;

                    cards.forEach(card => {
                        const price = Number(card.dataset.price);
                        const visible = !max || price <= max;
                        card.style.display = visible ? '' : 'none';
                        if (visible) nbVisible++;
                    });

                    // Gestion du message "Aucun lieu"
                    let msg = document.getElementById('msg-vide');
                    if (nbVisible === 0) {
                        if (!msg) {
                            msg = document.createElement('p');
                            msg.id = 'msg-vide';
                            msg.textContent = "Aucun lieu ne correspond à ce critère.";
                            msg.style.color = "gray";
                            placesList.appendChild(msg);
                        }
                    } else if (msg) {
                        msg.remove();
                    }
                });
            })
            .catch(err => {
                placesList.innerHTML = `<p>Erreur lors du chargement des lieux : ${err.message}</p>`;
                console.error(err);
            });
    }

    // -----------------------------------------
    // PAGE DETAILS (place.html) : infos lieu, avis, formulaire avis
    // -----------------------------------------
    const placeDetailsSection = document.querySelector('.place-details');
    if (placeDetailsSection) {
        // Extraction place_id depuis URL
        function getPlaceIdFromUrl() {
            const params = new URLSearchParams(window.location.search);
            return params.get('id');
        }
        
        const placeId = getPlaceIdFromUrl();
        if (!placeId) {
            const placeInfo = document.querySelector('.place-info');
            if (placeInfo) placeInfo.innerHTML = "<p>Lieu inconnu</p>";
            return;
        }

        // Charge infos lieu + avis
        function fetchPlaceAndReviews() {
            const fetchOptions = jwt ? { 
                headers: { 'Authorization': 'Bearer ' + jwt },
                credentials: 'include'
            } : {};

            // Infos lieu
            fetch(`http://localhost:5001/api/v1/places/${placeId}`, fetchOptions)
                .then(resp => {
                    if (!resp.ok) throw new Error("Lieu introuvable");
                    return resp.json();
                })
                .then(place => {
                    const infoDiv = document.querySelector('.place-info');
                    if (infoDiv) {
                        infoDiv.innerHTML = `
                            <h1>${place.name} (${place.city_name || ""})</h1>
                            <p>Hébergé par <span class="host">${place.host_name || "Inconnu"}</span></p>
                            <p class="place-price">Prix : ${place.price_by_night} €/nuit</p>
                            <p>Description : ${place.description || ''}</p>
                            <ul>
                                ${(place.amenities || []).map(am => `<li>${am.name}</li>`).join('')}
                            </ul>
                        `;
                    }
                })
                .catch(err => {
                    const infoDiv = document.querySelector('.place-info');
                    if (infoDiv) infoDiv.innerHTML = `<p>${err.message}</p>`;
                });

            // Avis lieu
            fetch(`http://localhost:5001/api/v1/places/${placeId}/reviews/`, fetchOptions)
                .then(resp => resp.json())
                .then(reviews => {
                    const listDiv = document.getElementById('review-list');
                    if (!listDiv) return;
                    listDiv.innerHTML = '';
                    if (reviews.length === 0) {
                        listDiv.innerHTML = "<p>Aucun avis pour ce lieu.</p>";
                        return;
                    }
                    reviews.forEach(rv => {
                        const reviewCard = document.createElement('div');
                        reviewCard.className = 'review-card';
                        reviewCard.innerHTML = `
                            <p class="review-comment">${rv.text}</p>
                            <p class="review-user">Par ${rv.user_name || "Utilisateur inconnu"}</p>
                            <p class="review-rating">Note : ${rv.rating}/5</p>
                        `;
                        listDiv.appendChild(reviewCard);
                    });
                })
                .catch(err => {
                    const listDiv = document.getElementById('review-list');
                    if (listDiv) listDiv.innerHTML = `<p>Erreur chargement des avis : ${err.message}</p>`;
                });
        }
        fetchPlaceAndReviews();

        // Formulaire ajout avis
        const addReviewSection = document.getElementById('add-review');
        const reviewForm = document.getElementById('review-form');

        if (jwt) {
            if (addReviewSection) addReviewSection.style.display = 'block';

            if (reviewForm) {
                reviewForm.addEventListener('submit', (e) => {
                    e.preventDefault();

                    const text = document.getElementById('review-text').value.trim();
                    const rating = document.getElementById('review-rating').value;

                    if (!text || !rating) {
                        alert("Merci de remplir tous les champs.");
                        return;
                    }

                    fetch(`http://localhost:5001/api/v1/places/${placeId}/reviews/`, {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + jwt
                        },
                        body: JSON.stringify({ text, rating })
                    })
                        .then(resp => {
                            if (!resp.ok) throw new Error("Erreur lors de l'envoi de l'avis.");
                            return resp.json();
                        })
                        .then(() => {
                            reviewForm.reset();
                            fetchPlaceAndReviews();
                        })
                        .catch(err => {
                            alert(err.message || "Erreur inconnue");
                        });
                });
            }
        } else if (addReviewSection) {
            addReviewSection.innerHTML = `
                <a href="login.html" style="color: #007bff;">Connectez-vous pour laisser un avis</a>
            `;
        }
    }
});
