document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------
    // OUTIL : lire un cookie par son nom
    // -----------------------------------
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    // Récupération du JWT une seule fois au début
    const jwt = getCookie('jwt');

    // -----------------------------------------
    // GESTION BOUTON CONNEXION / DÉCONNEXION
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
                document.cookie = "jwt=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax";
                window.location.replace('index.html');
            });
        } else {
            newLoginBtn.textContent = "Connexion";
            newLoginBtn.href = "login.html";
        }
    }

    // FONCTION DE CONNEXION RAPIDE POUR LES COMPTES DE TEST
    window.quickLogin = function(email, password) {
        // Pré-remplir les champs
        document.getElementById('email').value = email;
        document.getElementById('password').value = password;
        
        // Simuler la soumission du formulaire
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            // Animation visuelle
            const button = document.querySelector('.login-button-submit');
            if (button) {
                button.textContent = 'Connexion en cours...';
                button.classList.add('loading');
            }
            
            // Déclencher la soumission après un petit délai pour l'animation
            setTimeout(() => {
                loginForm.dispatchEvent(new Event('submit'));
            }, 500);
        }
    };

// --------------------------------------------
// GESTION NAVIGATION SELON LE RÔLE UTILISATEUR  
// --------------------------------------------
if (jwt) {
    // Décoder le JWT pour récupérer les informations utilisateur
    try {
        const tokenParts = jwt.split('.');
        const payload = JSON.parse(atob(tokenParts[1]));
        
        // DEBUG COMPLET pour identifier le problème
        console.log('=== DEBUG NAVIGATION SCRIPTS.JS ===');
        console.log('Payload JWT:', payload);
        console.log('Rôle brut:', payload.role);
        console.log('Type du rôle:', typeof payload.role);
        console.log('==============================');
        
        const userRole = payload.role;
        
        // VÉRIFICATION ROBUSTE DU RÔLE PROPRIÉTAIRE
        if (isOwner(userRole)) {
            console.log('Utilisateur reconnu comme propriétaire');
            addOwnerNavigation();
        } else {
            console.log('Utilisateur non reconnu comme propriétaire. Rôle:', userRole);
        }
    } catch (e) {
        console.error('Erreur décodage JWT pour navigation:', e);
    }
}

// FONCTION UNIVERSELLE DE VÉRIFICATION DU RÔLE
function isOwner(role) {
    if (!role) {
        console.log('Rôle vide ou undefined');
        return false;
    }
    
    const cleanRole = role.toString().toLowerCase().trim();
    const ownerRoles = ['owner', 'propriétaire', 'proprietaire', 'propri'];
    
    console.log('Rôle nettoyé:', cleanRole);
    console.log('Est propriétaire:', ownerRoles.includes(cleanRole));
    
    return ownerRoles.includes(cleanRole);
}

function addOwnerNavigation() {
    const nav = document.querySelector('.nav-container');
    if (nav && !document.getElementById('owner-nav-added')) {
        console.log('🏠 Ajout des liens propriétaire dans la navigation');
        
        const ownerLinks = document.createElement('div');
        ownerLinks.id = 'owner-nav-added';
        ownerLinks.className = 'owner-navigation';
        ownerLinks.innerHTML = `
            <a href="create-place.html" class="nav-link owner-link">
                Créer un lieu
            </a>
            <a href="my-places.html" class="nav-link owner-link">
                 Mes lieux
            </a>
        `;
        
        // Insérer avant le bouton de connexion/déconnexion
        const loginBtn = document.querySelector('.login-button');
        if (loginBtn) {
            nav.insertBefore(ownerLinks, loginBtn);
        } else {
            // Si pas de bouton login, ajouter à la fin de nav-links
            const navLinks = document.querySelector('.nav-links');
            if (navLinks) {
                navLinks.appendChild(ownerLinks);
            }
        }
        
        console.log('Liens propriétaire ajoutés avec succès');
    } else if (document.getElementById('owner-nav-added')) {
        console.log('Liens propriétaire déjà présents');
    } else {
        console.log('Navigation container non trouvé');
    }
}


    // ---------------------------------------------------
    // PAGE LOGIN : gestion formulaire connexion + erreurs
    // ---------------------------------------------------
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
                        document.cookie = `jwt=${data.access_token}; path=/; SameSite=Lax`;
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

// -------------------------------------------------
// ✅ PAGE REGISTER : gestion formulaire inscription
// -------------------------------------------------
const registerForm = document.getElementById('register-form');
const registerError = document.getElementById('register-error');
const registerSuccess = document.getElementById('register-success');

if (registerForm) {
    registerForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Récupération des données du formulaire
        const formData = {
            first_name: document.getElementById('first_name').value.trim(),
            last_name: document.getElementById('last_name').value.trim(),
            username: document.getElementById('username').value.trim(),
            email: document.getElementById('email').value.trim(),
            password: document.getElementById('password').value,
            role: document.getElementById('role').value
        };

        // Validation basique côté client
        if (!formData.first_name || !formData.last_name || !formData.username || !formData.email || !formData.password) {
            if (registerError) {
                registerError.textContent = 'Tous les champs sont obligatoires';
                registerError.style.display = 'block';
            }
            return;
        }

        try {
            // Masquer les messages précédents
            if (registerError) registerError.style.display = 'none';
            if (registerSuccess) registerSuccess.style.display = 'none';

            // Désactiver le bouton pendant la requête
            const submitButton = registerForm.querySelector('button[type="submit"]');
            const originalText = submitButton?.textContent || 'S\'inscrire';
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Inscription en cours...';
            }

            const response = await fetch('http://localhost:5001/api/v1/users/register', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const data = await response.json();
                
                // CONNEXION AUTOMATIQUE après inscription
                try {
                    if (registerSuccess) {
                        registerSuccess.textContent = 'Inscription réussie ! Connexion automatique...';
                        registerSuccess.style.display = 'block';
                    }
                    
                    const loginResponse = await fetch('http://localhost:5001/api/v1/users/login', {
                        method: 'POST',
                        credentials: 'include',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: formData.email,
                            password: formData.password
                        })
                    });
                    
                    if (loginResponse.ok) {
                        const loginData = await loginResponse.json();
                        if (loginData.token) {
                            document.cookie = `jwt=${loginData.token}; path=/; SameSite=Lax`;
                            
                            if (registerSuccess) {
                                registerSuccess.textContent = 'Inscription et connexion réussies ! Redirection...';
                                registerSuccess.style.display = 'block';
                            }
                            
                            // Réinitialiser le formulaire
                            registerForm.reset();
                            
                            setTimeout(() => {
                                window.location.href = 'index.html';
                            }, 1500);
                            return;
                        }
                    }
                } catch (loginError) {
                    console.log('Connexion automatique échouée, redirection vers login');
                }
                
                // Si la connexion automatique échoue, comportement normal
                if (registerSuccess) {
                    registerSuccess.textContent = 'Inscription réussie ! Vous pouvez maintenant vous connecter.';
                    registerSuccess.style.display = 'block';
                }
                
                // Réinitialiser le formulaire
                registerForm.reset();
                
                // Rediriger vers la page de connexion après 2 secondes
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);

            } else {
                let errorMsg = 'Erreur lors de l\'inscription';
                try {
                    const errorData = await response.json();
                    if (errorData.error) {
                        errorMsg = errorData.error;
                    } else if (errorData.message) {
                        errorMsg = errorData.message;
                    }
                } catch (_) {}
                
                throw new Error(errorMsg);
            }
        } catch (error) {
            console.error('Erreur inscription:', error);
            if (registerError) {
                registerError.textContent = error.message || "Erreur de connexion au serveur";
                registerError.style.display = 'block';
            }
        } finally {
            // Réactiver le bouton
            const submitButton = registerForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        }
    });
}

    // ---------------------------------------------------------------
    // PAGE ACCUEIL (index.html) : affichage lieux + filtrage par prix
    // ---------------------------------------------------------------
    const placesList = document.getElementById('places-list');
    const priceFilter = document.getElementById('price-filter');

    if (placesList && priceFilter) {
        // Options pour l'authentification si connecté
        const options = jwt ? { 
            headers: { 'Authorization': 'Bearer ' + jwt },
            credentials: 'include'
        } : {};

        // Appel API simple
        fetch('http://localhost:5001/api/v1/places/', options)
            .then(response => response.json())
            .then(places => {
                // Vider la liste
                placesList.innerHTML = '';

                // Créer une carte pour chaque lieu
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

                // Créer les options de filtre prix
                const prices = [...new Set(places.map(p => p.price_by_night))].sort((a, b) => a - b);
                priceFilter.innerHTML = '<option value="">Tous</option>' + 
                    prices.map(price => `<option value="${price}">≤ ${price} €</option>`).join('');

                // Gestion du filtre
                priceFilter.addEventListener('change', () => {
                    const maxPrice = Number(priceFilter.value);
                    document.querySelectorAll('.place-card').forEach(card => {
                        const cardPrice = Number(card.dataset.price);
                        card.style.display = (!maxPrice || cardPrice <= maxPrice) ? '' : 'none';
                    });
                });
            })
            .catch(error => {
                placesList.innerHTML = '<p>Erreur de chargement des lieux</p>';
                console.error('Erreur:', error);
            });
    }

    // -------------------------------------------------------------
    // ✅ PAGE CREATE PLACE - Formulaire de création avec validation
    // -------------------------------------------------------------
    const createPlaceForm = document.getElementById('create-place-form');
    const createPlaceError = document.getElementById('create-place-error');
    const createPlaceSuccess = document.getElementById('create-place-success');

    if (createPlaceForm) {
        if (!jwt) {
            document.body.innerHTML = `
                <div style="text-align: center; margin-top: 50px;">
                    <h2>Accès refusé</h2>
                    <p>Vous devez être connecté pour créer un lieu.</p>
                    <a href="login.html" style="color: #007bff;">Se connecter</a>
                </div>
            `;
            return;
        }

        function loadAmenities() {
            const amenitiesContainer = document.getElementById('amenities-container');
            if (!amenitiesContainer || amenitiesContainer.dataset.loaded === 'true') return;

            amenitiesContainer.innerHTML = '<div class="loading-amenities"><p>🔄 Chargement des équipements...</p></div>';

            fetch('http://localhost:5001/api/v1/amenities/', {
                headers: { 'Authorization': 'Bearer ' + jwt },
                credentials: 'include'
            })
            .then(resp => resp.json())
            .then(amenities => {
                amenitiesContainer.innerHTML = '';
                
                const uniqueAmenities = amenities.filter((amenity, index, self) => 
                    index === self.findIndex(a => a.id === amenity.id)
                );

                uniqueAmenities.forEach(amenity => {
                    const checkboxDiv = document.createElement('div');
                    checkboxDiv.className = 'amenity-checkbox';
                    checkboxDiv.innerHTML = `
                        <label>
                            <input type="checkbox" name="amenities" value="${amenity.id}">
                            ${amenity.name}
                        </label>
                    `;
                    amenitiesContainer.appendChild(checkboxDiv);
                });

                amenitiesContainer.dataset.loaded = 'true';
            })
            .catch(err => {
                amenitiesContainer.innerHTML = '<p style="color: #dc3545;">❌ Erreur chargement équipements</p>';
            });
        }

        loadAmenities();

        // Fonctions de validation
        function showFieldError(errorId, message) {
            const errorSpan = document.getElementById(errorId);
            if (errorSpan) {
                errorSpan.textContent = message;
                errorSpan.style.display = 'block';
            }
        }

        function hideFieldError(errorId) {
            const errorSpan = document.getElementById(errorId);
            if (errorSpan) {
                errorSpan.style.display = 'none';
            }
        }

        function clearFieldError(input, errorId) {
            if (input && input.classList.contains('error')) {
                input.classList.remove('error');
                hideFieldError(errorId);
            }
        }

        // Validation en temps réel
        const titleInput = document.getElementById('place-title');
        const priceInput = document.getElementById('place-price');
        const latitudeInput = document.getElementById('place-latitude');
        const longitudeInput = document.getElementById('place-longitude');

        if (titleInput) {
            titleInput.addEventListener('input', () => clearFieldError(titleInput, 'title-error'));
            titleInput.addEventListener('blur', () => {
                const value = titleInput.value.trim();
                if (!value) {
                    showFieldError('title-error', 'Le titre est obligatoire');
                    titleInput.classList.add('error');
                } else if (value.length < 3) {
                    showFieldError('title-error', 'Le titre doit contenir au moins 3 caractères');
                    titleInput.classList.add('error');
                } else {
                    hideFieldError('title-error');
                    titleInput.classList.remove('error');
                }
            });
        }

        if (priceInput) {
            priceInput.addEventListener('input', () => clearFieldError(priceInput, 'price-error'));
            priceInput.addEventListener('blur', () => {
                const value = parseFloat(priceInput.value);
                if (!priceInput.value) {
                    showFieldError('price-error', 'Le prix est obligatoire');
                    priceInput.classList.add('error');
                } else if (isNaN(value) || value <= 0) {
                    showFieldError('price-error', 'Le prix doit être un nombre positif');
                    priceInput.classList.add('error');
                } else {
                    hideFieldError('price-error');
                    priceInput.classList.remove('error');
                }
            });
        }

        if (latitudeInput) {
            latitudeInput.addEventListener('input', () => clearFieldError(latitudeInput, 'latitude-error'));
            latitudeInput.addEventListener('blur', () => {
                const value = parseFloat(latitudeInput.value);
                if (!latitudeInput.value.trim()) {
                    showFieldError('latitude-error', 'La latitude est obligatoire');
                    latitudeInput.classList.add('error');
                } else if (isNaN(value) || value < -90 || value > 90) {
                    showFieldError('latitude-error', 'La latitude doit être entre -90 et 90');
                    latitudeInput.classList.add('error');
                } else {
                    hideFieldError('latitude-error');
                    latitudeInput.classList.remove('error');
                }
            });
        }

        if (longitudeInput) {
            longitudeInput.addEventListener('input', () => clearFieldError(longitudeInput, 'longitude-error'));
            longitudeInput.addEventListener('blur', () => {
                const value = parseFloat(longitudeInput.value);
                if (!longitudeInput.value.trim()) {
                    showFieldError('longitude-error', 'La longitude est obligatoire');
                    longitudeInput.classList.add('error');
                } else if (isNaN(value) || value < -180 || value > 180) {
                    showFieldError('longitude-error', 'La longitude doit être entre -180 et 180');
                    longitudeInput.classList.add('error');
                } else {
                    hideFieldError('longitude-error');
                    longitudeInput.classList.remove('error');
                }
            });
        }

        // Soumission du formulaire
        createPlaceForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            if (createPlaceError) createPlaceError.style.display = 'none';
            if (createPlaceSuccess) createPlaceSuccess.style.display = 'none';

            const formData = new FormData(createPlaceForm);
            const selectedAmenities = Array.from(document.querySelectorAll('input[name="amenities"]:checked'))
                .map(checkbox => checkbox.value);

            const placeData = {
                title: (formData.get('title') || '').trim(),
                description: (formData.get('description') || '').trim(),
                price: parseFloat(formData.get('price') || '0'),
                latitude: parseFloat(formData.get('latitude') || '0'),
                longitude: parseFloat(formData.get('longitude') || '0'),
                amenities: selectedAmenities
            };

            // Validation finale
            const validationErrors = [];
            
            if (!placeData.title || placeData.title.length < 3) {
                validationErrors.push('Le titre doit contenir au moins 3 caractères');
            }
            
            if (!placeData.price || placeData.price <= 0) {
                validationErrors.push('Le prix doit être un nombre positif');
            }
            
            if (isNaN(placeData.latitude) || placeData.latitude < -90 || placeData.latitude > 90) {
                validationErrors.push('Latitude invalide (doit être entre -90 et 90)');
            }
            
            if (isNaN(placeData.longitude) || placeData.longitude < -180 || placeData.longitude > 180) {
                validationErrors.push('Longitude invalide (doit être entre -180 et 180)');
            }

            if (validationErrors.length > 0) {
                if (createPlaceError) {
                    createPlaceError.innerHTML = validationErrors.join('<br>');
                    createPlaceError.style.display = 'block';
                }
                return;
            }

            try {
                const submitButton = createPlaceForm.querySelector('button[type="submit"]');
                const originalText = submitButton?.textContent || 'Créer le lieu';
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = 'Création en cours...';
                }

                const response = await fetch('http://localhost:5001/api/v1/places/', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + jwt
                    },
                    body: JSON.stringify(placeData)
                });

                if (response.ok) {
                    const newPlace = await response.json();
                    
                    if (createPlaceSuccess) {
                        createPlaceSuccess.innerHTML = `
                            <strong>Succès !</strong> Votre lieu "${newPlace.name || newPlace.title}" a été créé avec succès.
                            <br><a href="place.html?id=${newPlace.id}">Voir le lieu créé</a>
                        `;
                        createPlaceSuccess.style.display = 'block';
                    }
                    
                    createPlaceForm.reset();
                    document.querySelectorAll('input[name="amenities"]').forEach(cb => cb.checked = false);
                    
                    setTimeout(() => {
                        window.location.href = `place.html?id=${newPlace.id}`;
                    }, 3000);
                    
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Erreur lors de la création');
                }
            } catch (error) {
                if (createPlaceError) {
                    createPlaceError.textContent = error.message;
                    createPlaceError.style.display = 'block';
                }
            } finally {
                const submitButton = createPlaceForm.querySelector('button[type="submit"]');
                const originalText = 'Créer le lieu';
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }
            }
        });
    }

    // ---------------------------------------------------------------------
    // PAGE MES LIEUX (my-places.html) - MAINTENANT DANS DOMContentLoaded
    // ---------------------------------------------------------------------
    const myPlacesList = document.getElementById('my-places-list');
    const myPlacesStats = document.getElementById('my-places-stats');
    const noPlacesMessage = document.getElementById('no-places-message');
    const myPlacesError = document.getElementById('my-places-error');
    const myPlacesSuccess = document.getElementById('my-places-success');

    if (myPlacesList) {
        if (!jwt) {
            document.body.innerHTML = `
                <div style="text-align: center; margin-top: 50px;">
                    <h2>Accès refusé</h2>
                    <p>Vous devez être connecté pour voir vos lieux.</p>
                    <a href="login.html" style="color: #007bff;">Se connecter</a>
                </div>
            `;
            return;
        }

        async function loadMyPlaces() {
            try {
                myPlacesList.innerHTML = '<div class="loading-places"><p>🔄 Chargement de vos lieux...</p></div>';
                
                const response = await fetch('http://localhost:5001/api/v1/places/', {
                    headers: { 'Authorization': 'Bearer ' + jwt },
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error(`Erreur API: ${response.status}`);
                }

                const allPlaces = await response.json();
                
                // Décoder le JWT pour récupérer l'ID utilisateur
                const tokenParts = jwt.split('.');
                const payload = JSON.parse(atob(tokenParts[1]));
                const currentUserId = payload.sub;
                
                const myPlaces = allPlaces.filter(place => place.owner_id === currentUserId);
                
                if (myPlaces.length === 0) {
                    myPlacesList.innerHTML = '';
                    noPlacesMessage.style.display = 'block';
                    myPlacesStats.style.display = 'none';
                } else {
                    displayMyPlaces(myPlaces);
                    displayStats(myPlaces);
                    noPlacesMessage.style.display = 'none';
                    myPlacesStats.style.display = 'grid';
                }
                
            } catch (error) {
                console.error(' Erreur chargement mes lieux:', error);
                myPlacesList.innerHTML = '';
                if (myPlacesError) {
                    myPlacesError.textContent = `Erreur: ${error.message}`;
                    myPlacesError.style.display = 'block';
                }
            }
        }

        function displayMyPlaces(places) {
            myPlacesList.innerHTML = '';
            
            places.forEach(place => {
                const placeCard = document.createElement('div');
                placeCard.className = 'my-place-card';
                
                const amenitiesHtml = (place.amenities || [])
                    .slice(0, 3)
                    .map(amenity => `<span class="amenity-tag">${amenity.name}</span>`)
                    .join('');
                
                const moreAmenities = (place.amenities?.length || 0) > 3 
                    ? `<span class="amenity-tag">+${(place.amenities.length - 3)} autres</span>` 
                    : '';
                
                placeCard.innerHTML = `
                    <div class="my-place-card-content">
                        <h3>${place.name}</h3>
                        <div class="my-place-card-info">
                            <p class="place-price">${place.price_by_night} €/nuit</p>
                            <p><strong>Latitude:</strong> ${place.latitude}</p>
                            <p><strong>Longitude:</strong> ${place.longitude}</p>
                            <p><strong>Description:</strong> ${place.description || 'Aucune description'}</p>
                        </div>
                        <div class="place-amenities">
                            ${amenitiesHtml}
                            ${moreAmenities}
                        </div>
                        <div class="my-place-card-actions">
                            <a href="place.html?id=${place.id}" class="btn btn-secondary">
                                👁️ Voir
                            </a>
                            <button onclick="editPlace('${place.id}')" class="btn btn-primary">
                                ✏️ Éditer
                            </button>
                            <button onclick="confirmDeletePlace('${place.id}', '${place.name}')" class="btn btn-danger">
                                🗑️ Supprimer
                            </button>
                        </div>
                    </div>
                `;
                
                myPlacesList.appendChild(placeCard);
            });
        }

        function displayStats(places) {
            const totalPlaces = places.length;
            const totalPrice = places.reduce((sum, place) => sum + (place.price_by_night || 0), 0);
            const averagePrice = totalPlaces > 0 ? (totalPrice / totalPlaces).toFixed(0) : 0;
            const totalReviews = places.reduce((sum, place) => sum + (place.reviews?.length || 0), 0);
            
            document.getElementById('total-places').textContent = totalPlaces;
            document.getElementById('average-price').textContent = `${averagePrice} €`;
            document.getElementById('total-reviews').textContent = totalReviews;
        }

        // Fonctions globales pour les boutons
        window.editPlace = function(placeId) {
            window.location.href = `edit-place.html?id=${placeId}`;
        };

        let placeToDelete = null;
        
        window.confirmDeletePlace = function(placeId, placeName) {
            placeToDelete = placeId;
            document.getElementById('delete-place-name').textContent = placeName;
            document.getElementById('delete-modal').style.display = 'flex';
        };

        // Gestion du modal de suppression
        const deleteModal = document.getElementById('delete-modal');
        const cancelDeleteBtn = document.getElementById('cancel-delete');
        const confirmDeleteBtn = document.getElementById('confirm-delete');

        if (cancelDeleteBtn) {
            cancelDeleteBtn.addEventListener('click', () => {
                deleteModal.style.display = 'none';
                placeToDelete = null;
            });
        }

        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', async () => {
                if (placeToDelete) {
                    await deletePlace(placeToDelete);
                    deleteModal.style.display = 'none';
                    placeToDelete = null;
                }
            });
        }

        if (deleteModal) {
            deleteModal.addEventListener('click', (e) => {
                if (e.target === deleteModal) {
                    deleteModal.style.display = 'none';
                    placeToDelete = null;
                }
            });
        }

        async function deletePlace(placeId) {
            try {
                confirmDeleteBtn.disabled = true;
                confirmDeleteBtn.textContent = 'Suppression...';
                
                const response = await fetch(`http://localhost:5001/api/v1/places/${placeId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': 'Bearer ' + jwt },
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error('Erreur lors de la suppression');
                }

                if (myPlacesSuccess) {
                    myPlacesSuccess.textContent = 'Lieu supprimé avec succès !';
                    myPlacesSuccess.style.display = 'block';
                    setTimeout(() => {
                        myPlacesSuccess.style.display = 'none';
                    }, 3000);
                }

                loadMyPlaces();

            } catch (error) {
                console.error('Erreur suppression:', error);
                if (myPlacesError) {
                    myPlacesError.textContent = `Erreur suppression: ${error.message}`;
                    myPlacesError.style.display = 'block';
                }
            } finally {
                confirmDeleteBtn.disabled = false;
                confirmDeleteBtn.textContent = 'Supprimer';
            }
        }

        loadMyPlaces();
    }

    // -----------------------------------------------------------------------
    // PAGE EDIT PLACE (edit-place.html) - MAINTENANT DANS DOMContentLoaded  
    // -----------------------------------------------------------------------
    const editPlaceForm = document.getElementById('edit-place-form');
    const editPlaceError = document.getElementById('edit-place-error');
    const editPlaceSuccess = document.getElementById('edit-place-success');
    const editPlaceLoading = document.getElementById('edit-place-loading');

    if (editPlaceForm) {
        if (!jwt) {
            document.body.innerHTML = `
                <div style="text-align: center; margin-top: 50px;">
                    <h2>Accès refusé</h2>
                    <p>Vous devez être connecté pour éditer un lieu.</p>
                    <a href="login.html" style="color: #007bff;">Se connecter</a>
                </div>
            `;
            return;
        }

        function getPlaceIdFromUrl() {
            const params = new URLSearchParams(window.location.search);
            return params.get('id');
        }

        const placeId = getPlaceIdFromUrl();
        if (!placeId) {
            document.body.innerHTML = `
                <div style="text-align: center; margin-top: 50px;">
                    <h2>Lieu introuvable</h2>
                    <p>Aucun identifiant de lieu fourni.</p>
                    <a href="my-places.html" style="color: #007bff;">Retour à mes lieux</a>
                </div>
            `;
            return;
        }

        let originalPlaceData = {};
        let currentUserId = null;

        try {
            const tokenParts = jwt.split('.');
            const payload = JSON.parse(atob(tokenParts[1]));
            currentUserId = payload.sub;
        } catch (e) {
            console.error('Erreur décodage JWT:', e);
        }

        async function loadPlaceData() {
            try {
                editPlaceLoading.style.display = 'block';
                editPlaceForm.style.display = 'none';

                const response = await fetch(`http://localhost:5001/api/v1/places/${placeId}`, {
                    headers: { 'Authorization': 'Bearer ' + jwt },
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error(`Lieu introuvable (${response.status})`);
                }

                const place = await response.json();

                if (place.owner_id !== currentUserId) {
                    throw new Error('Vous n\'êtes pas autorisé à éditer ce lieu');
                }

                originalPlaceData = {
                    title: place.name || '',
                    description: place.description || '',
                    price: place.price_by_night || 0,
                    latitude: place.latitude || 0,
                    longitude: place.longitude || 0,
                    amenities: (place.amenities || []).map(a => a.id ? a.id.toString() : a.toString())
                };

                await populateForm(place);
                editPlaceLoading.style.display = 'none';
                editPlaceForm.style.display = 'block';

            } catch (error) {
                console.error('Erreur chargement lieu:', error);
                editPlaceLoading.style.display = 'none';
                
                document.body.innerHTML = `
                    <div style="text-align: center; margin-top: 50px;">
                        <h2>Erreur</h2>
                        <p>${error.message}</p>
                        <a href="my-places.html" style="color: #007bff;">Retour à mes lieux</a>
                    </div>
                `;
            }
        }

        loadPlaceData();
    }

    // -------------------------------------------------------------
    // PAGE DETAILS (place.html) : infos lieu, avis, formulaire avis
    // ------------------------------------------------------------
    const placeDetailsSection = document.querySelector('.place-card-main');
    if (placeDetailsSection || document.getElementById('place-loading')) {
        
        function getPlaceIdFromUrl() {
            const params = new URLSearchParams(window.location.search);
            return params.get('id');
        }
        
        const placeId = getPlaceIdFromUrl();
        if (!placeId) {
            document.querySelector('.container').innerHTML = `
                <div style="text-align: center; margin-top: 50px;">
                    <h2>Lieu introuvable</h2>
                    <p>Aucun identifiant de lieu fourni.</p>
                    <a href="index.html" style="color: #007bff;">Retour à l'accueil</a>
                </div>
            `;
            return;
        }

        function loadReviews() {
            console.log('Chargement des avis...');
            
            const fetchOptions = jwt ? { 
                headers: { 'Authorization': 'Bearer ' + jwt },
                credentials: 'include'
            } : {};
            
            fetch(`http://localhost:5001/api/v1/places/${placeId}/reviews/`, fetchOptions)
                .then(resp => resp.json())
                .then(reviews => {
                    const listDiv = document.getElementById('review-list');
                    if (!listDiv) return;
                    
                    listDiv.innerHTML = '';
                    
                    if (reviews.length === 0) {
                        listDiv.innerHTML = `
                            <div class="no-reviews" style="text-align: center; padding: 40px; background: #f8f9fa; border-radius: 10px; margin: 20px 0;">
                                <div style="font-size: 3rem; margin-bottom: 15px;">💭</div>
                                <h3 style="color: #6c757d; margin-bottom: 10px;">Aucun avis pour le moment</h3>
                                <p style="color: #6c757d;">Soyez le premier à partager votre expérience !</p>
                            </div>
                        `;
                        return;
                    }
                    
                    reviews.forEach(rv => {
                        const reviewCard = document.createElement('div');
                        reviewCard.className = 'review-card';
                        reviewCard.innerHTML = `
                            <div class="review-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <span class="review-user" style="font-weight: 600; color: #333;">👤 ${rv.user_name || "Utilisateur inconnu"}</span>
                                <span class="review-rating" style="background: #ffc107; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">⭐ ${rv.rating}/5</span>
                            </div>
                            <p class="review-comment" style="color: #555; line-height: 1.5; margin: 0;">${rv.text}</p>
                        `;
                        listDiv.appendChild(reviewCard);
                    });
                })
                .catch(err => {
                    const listDiv = document.getElementById('review-list');
                    if (listDiv) {
                        listDiv.innerHTML = `<p style="color: #dc3545; text-align: center; padding: 20px;">Erreur chargement des avis : ${err.message}</p>`;
                    }
                });
        }

        function fetchPlaceAndReviews() {
            const fetchOptions = jwt ? { 
                headers: { 'Authorization': 'Bearer ' + jwt },
                credentials: 'include'
            } : {};

            // Chargement des détails du lieu
            fetch(`http://localhost:5001/api/v1/places/${placeId}`, fetchOptions)
                .then(resp => {
                    if (!resp.ok) throw new Error("Lieu introuvable");
                    return resp.json();
                })
                .then(place => {
                    console.log('Lieu chargé:', place);

                    // Masquer le loading et afficher le contenu
                    const loadingEl = document.getElementById('place-loading');
                    const cardEl = document.querySelector('.place-card-main');
                    
                    if (loadingEl) loadingEl.style.display = 'none';
                    if (cardEl) cardEl.style.display = 'block';

                    // Remplir les informations du lieu
                    const infoDiv = document.querySelector('.place-info');
                    if (infoDiv) {
                        infoDiv.innerHTML = `
                            <h1>${place.name}</h1>
                            <p>Hébergé par <span class="host">${place.host_name || "Inconnu"}</span></p>
                            <p class="place-price">${place.price_by_night} €/nuit</p>
                            <p><strong>Description :</strong> ${place.description || 'Aucune description'}</p>
                            <div class="amenities">
                                <strong>Équipements :</strong>
                                <ul>
                                    ${(place.amenities || []).map(am => `<li>${am.name}</li>`).join('')}
                                </ul>
                            </div>
                        `;
                    }

                    loadReviews();
                })
                .catch(err => {
                    console.error('Erreur:', err);
                    const loadingEl = document.getElementById('place-loading');
                    const errorEl = document.getElementById('place-error');
                    
                    if (loadingEl) loadingEl.style.display = 'none';
                    if (errorEl) {
                        errorEl.textContent = err.message;
                        errorEl.style.display = 'block';
                    }
                });
        }
        
        // Charger immédiatement
        fetchPlaceAndReviews();

        // Gestion du formulaire d'avis
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
                        body: JSON.stringify({ text, rating: parseInt(rating) })
                    })
                        .then(resp => {
                            if (!resp.ok) throw new Error("Erreur lors de l'envoi de l'avis.");
                            return resp.json();
                        })
                        .then(() => {
                            reviewForm.reset();
                            loadReviews();
                        })
                        .catch(err => {
                            alert(err.message || "Erreur inconnue");
                        });
                });
            }
        } else if (addReviewSection) {
            addReviewSection.innerHTML = `
                <div class="login-prompt-content">
                    <h3> Connectez-vous pour laisser un avis</h3>
                    <a href="login.html" class="btn btn-primary">Se connecter</a>
                </div>
            `;
        }
    }
});
