#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère l'arbre généalogique interactif (HTML autonome) à partir du fichier JSON.

Usage :
    python generer_arbre.py                      -> lit genealogie_samuel.json
    python generer_arbre.py mon_fichier.json     -> lit le fichier indiqué
    (ou glisser-déposer le .json sur Generer_Arbre.bat)

PHOTOS
    Déposez les images dans le sous-dossier « photos », nommées d'après
    l'identifiant de la personne : photos/pierre-jean-1645.jpg
    Elles sont redimensionnées et intégrées dans le HTML, qui reste
    un fichier unique, autonome et transportable.
    Sans photo, la personne reçoit un médaillon à initiales.

Le HTML produit ne requiert aucune connexion ni bibliothèque externe.
"""

import base64
import io
import json
import mimetypes
import re
import sys
from pathlib import Path

EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")
COTE_MAX = 420          # pixels : taille maximale du portrait intégré
COTE_GALERIE = 1400     # pixels : plus grand côté d'une photo de galerie
QUALITE = 82

GABARIT = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITRE__</title>
<style>
:root{
  --bg:#f8f5ec; --surface:#fffdf7; --surface-2:#f0e9d9; --surface-3:#e7dec8;
  --ink:#241f17; --muted:#6b6150; --faint:#9b9079;
  --line:#cfc3a9; --line-soft:#e4dbc7;
  --jean:#2f5d8f; --trinh:#2f7d4f; --gagne:#7c5a86;
  --or:#b4862c; --or-clair:#e0b65c; --or-bg:#f8edd4;
  --fr:#b08a3e; --fr-bg:#f6ecd6;
  --nf:#2f7d4f; --nf-bg:#dff0e4;
  --alerte:#a8452a; --alerte-bg:#f9e4dd;
  --ombre:0 1px 2px rgba(60,45,25,.10), 0 6px 18px rgba(60,45,25,.07);
  --r:9px;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#15130e; --surface:#201d16; --surface-2:#2b2719; --surface-3:#36301f;
    --ink:#f3eee3; --muted:#a89c85; --faint:#79705d;
    --line:#474032; --line-soft:#332e24;
    --or:#dcae58; --or-clair:#f0cd8a; --or-bg:#34280f;
    --fr:#d2a85e; --fr-bg:#2e2412;
    --nf:#62c48f; --nf-bg:#152c1f;
    --alerte:#e08a6c; --alerte-bg:#36201a;
    --ombre:0 1px 2px rgba(0,0,0,.5), 0 6px 20px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  --bg:#15130e; --surface:#201d16; --surface-2:#2b2719; --surface-3:#36301f;
  --ink:#f3eee3; --muted:#a89c85; --faint:#79705d;
  --line:#474032; --line-soft:#332e24;
  --or:#dcae58; --or-clair:#f0cd8a; --or-bg:#34280f;
  --fr:#d2a85e; --fr-bg:#2e2412;
  --nf:#62c48f; --nf-bg:#152c1f;
  --alerte:#e08a6c; --alerte-bg:#36201a;
  --ombre:0 1px 2px rgba(0,0,0,.5), 0 6px 20px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  overflow:hidden; -webkit-font-smoothing:antialiased;
}
button,input{font:inherit;color:inherit}

/* ---------- barre du haut ---------- */
header{
  position:fixed; inset:0 0 auto 0; z-index:40; height:60px;
  display:flex; align-items:center; gap:14px; padding:0 16px;
  background:color-mix(in srgb, var(--surface) 93%, transparent);
  backdrop-filter:blur(10px); border-bottom:1px solid var(--line-soft);
}
.plaque{
  background:var(--surface-2); border:1px solid var(--line-soft);
  padding:6px 16px 7px; border-radius:3px; min-width:0;
  box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--surface) 70%, transparent);
}
.plaque b{display:block; font-size:16px; font-weight:600; letter-spacing:.3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.plaque span{display:block; font-size:11px; color:var(--muted); letter-spacing:.2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.espace{flex:1}
.outils{display:flex;align-items:center;gap:7px;flex-shrink:0}
.btn{
  border:1px solid var(--line); background:var(--surface); border-radius:var(--r);
  padding:7px 11px; font-size:12.5px; cursor:pointer; white-space:nowrap;
  transition:background .14s, border-color .14s, color .14s;
}
.btn:hover{background:var(--surface-2)}
.btn[aria-pressed="true"]{background:var(--or-bg); border-color:var(--or); color:var(--or); font-weight:600}
.btn.rond{padding:7px 10px; font-variant-numeric:tabular-nums}
.bascule{display:flex; border:1px solid var(--line); border-radius:var(--r); overflow:hidden}
.bascule button{border:0; background:var(--surface); padding:7px 12px; font-size:12.5px; cursor:pointer}
.bascule button+button{border-left:1px solid var(--line)}
.bascule button[aria-pressed="true"]{background:var(--or-bg); color:var(--or); font-weight:600}
.recherche{position:relative}
.recherche input{
  width:188px; padding:7px 26px 7px 11px; border-radius:var(--r);
  border:1px solid var(--line); background:var(--surface); font-size:12.5px;
}
.recherche input:focus{outline:2px solid var(--or); outline-offset:-1px}
.recherche .effacer{
  position:absolute; right:4px; top:50%; transform:translateY(-50%);
  border:0; background:transparent; cursor:pointer; color:var(--faint);
  font-size:15px; line-height:1; padding:4px 5px; display:none;
}
.recherche.pleine .effacer{display:block}
.compteur{font-size:11.5px;color:var(--muted);min-width:54px;text-align:right;font-variant-numeric:tabular-nums}

/* ---------- toile ---------- */
#toile{position:fixed; inset:60px 0 0 0; cursor:grab; touch-action:none}
#toile.glisse{cursor:grabbing}
#toile svg{display:block;width:100%;height:100%}

.lien{fill:none; stroke:var(--line); stroke-width:1.5}
.lien.directe{stroke:var(--or); stroke-width:2.6}
.alliance{fill:none; stroke:var(--line); stroke-width:1.5}
.alliance.directe{stroke:var(--or); stroke-width:2.6}
.etiq-mariage{font-size:9.8px; fill:var(--faint); font-variant-numeric:tabular-nums}
.ruban{font-size:11.5px; fill:var(--faint); font-style:italic; letter-spacing:.3px}

/* ---------- médaillons ---------- */
.puce{cursor:pointer}
.plier{cursor:pointer}
.plier rect{fill:var(--surface); stroke:var(--line); stroke-width:1}
.plier text{font-size:9.6px; font-weight:700; fill:var(--muted);
  font-variant-numeric:tabular-nums; pointer-events:none}
.plier.ferme rect{fill:color-mix(in srgb, var(--or) 14%, var(--surface));
  stroke:var(--or)}
.plier.ferme text{fill:var(--or)}
.plier:hover rect{stroke:var(--or); stroke-width:2}
.anneau{fill:none; stroke-width:3.2; transition:stroke-width .14s}
.puce.fr .anneau{stroke:var(--fr)}
.j-br{font-weight:600}
.j-jean{background:color-mix(in srgb,var(--jean) 13%,transparent); color:var(--jean)}
.j-trinh{background:color-mix(in srgb,var(--trinh) 13%,transparent); color:var(--trinh)}
.j-gagne{background:color-mix(in srgb,var(--gagne) 13%,transparent); color:var(--gagne)}
.puce.nf .anneau{stroke:var(--nf)}
.puce.directe .anneau{stroke:var(--or); stroke-width:4.6}
/* APRÈS « directe », et c'est voulu : la lignée directe garde son anneau
   épais, mais c'est la BRANCHE qui en donne la couleur. Déclarées avant,
   ces règles étaient écrasées par la précédente à spécificité égale, et
   l'arbre sortait tout doré. */
.puce.br-jean  .anneau{stroke:var(--jean)}
.puce.br-trinh .anneau{stroke:var(--trinh)}
.puce.br-gagne .anneau{stroke:var(--gagne)}

.halo{fill:none; stroke:var(--or-clair); stroke-width:1.4; opacity:.55}
.disque{fill:var(--surface-2)}
.monogramme{font-size:21px; font-weight:600; fill:var(--faint); letter-spacing:.5px}
.puce:hover .anneau{stroke:var(--or); stroke-width:5}
.puce text.nom{font-size:11.4px; font-weight:600; fill:var(--ink)}
.puce.directe text.nom{fill:var(--or)}
/* Encore après « directe », pour la même raison que les anneaux. */
.puce.br-jean  text.nom{fill:var(--jean)}
.puce.br-trinh text.nom{fill:var(--trinh)}
.puce.br-gagne text.nom{fill:var(--gagne)}
.puce text.vie{font-size:9.8px; fill:var(--muted); font-variant-numeric:tabular-nums}
.puce.selectionne .anneau{stroke:var(--alerte); stroke-width:5}
.puce.eteint{opacity:.17}
.puce.trouve .anneau{stroke:var(--alerte); stroke-width:5}
/* Trait plein, même pour un noeud rattaché autrement. Les pointillés
   n'ajoutaient rien que la pastille rouge ne dise déjà, et ils donnaient à
   une moitié de l'arbre l'air d'être en sursis. */
.puce.detache .anneau{stroke-dasharray:none}

/* ---------- fiches (second mode) ---------- */
.puce rect.cadre{
  fill:var(--surface); stroke:var(--line); stroke-width:1.2; rx:8;
  transition:stroke .14s, stroke-width .14s;
}
.puce:hover rect.cadre{stroke:var(--or); stroke-width:2}
.puce.directe rect.cadre{stroke:var(--or); stroke-width:2; fill:var(--or-bg)}
.puce.ancetre rect.cadre{stroke-width:3}
.puce.detache rect.cadre{stroke-dasharray:none}
.puce.selectionne rect.cadre{stroke:var(--alerte); stroke-width:3}
.puce.trouve rect.cadre{stroke:var(--alerte); stroke-width:2.6}
.puce rect.bande{rx:2}
.puce.fr rect.bande{fill:var(--fr)}
.puce.nf rect.bande{fill:var(--nf)}
.puce text.nomf{font-size:12.6px; font-weight:600; fill:var(--ink)}
.puce text.vief{font-size:10.8px; fill:var(--muted); font-variant-numeric:tabular-nums}
.puce text.rang{font-size:10px; fill:var(--faint); font-style:italic}
.pastille{font-size:10px; font-weight:700; fill:#fff}
.pastille-fond{fill:var(--alerte)}

/* ---------- la fiche : carte flottante au clic sur un médaillon ---------- */
#fiche{
  position:fixed; z-index:50; width:322px; max-width:calc(100vw - 24px);
  background:var(--surface); border:1px solid var(--line); border-radius:12px;
  box-shadow:0 2px 6px rgba(60,45,25,.12), 0 18px 46px rgba(60,45,25,.20);
  opacity:0; visibility:hidden; transform:translateY(5px) scale(.985);
  transition:opacity .13s ease, transform .13s ease, visibility .13s; overflow:hidden;
}
#fiche.ouverte{opacity:1; visibility:visible; transform:none}
.f-haut{display:grid; grid-template-columns:auto 1fr auto; gap:0 12px; align-items:center;
  padding:13px 13px 12px 15px; border-bottom:1px solid var(--line-soft); background:var(--surface-2)}
.f-portrait{width:54px; height:54px; border-radius:50%; object-fit:cover;
  border:2.5px solid var(--or); background:var(--surface)}
.f-mono{width:54px; height:54px; border-radius:50%; background:var(--surface);
  border:2.5px solid var(--line); display:grid; place-items:center;
  font-size:17px; font-weight:600; color:var(--faint)}
.f-ident{min-width:0}
.f-ident h3{margin:0; font-size:16px; font-weight:600; line-height:1.2}
.f-dates{font-size:11.8px; color:var(--muted); font-variant-numeric:tabular-nums; margin-top:2px}
.f-surnom{font-size:11.4px; color:var(--faint); font-style:italic; margin-top:1px}
.f-fermer{border:0; background:transparent; cursor:pointer; color:var(--faint);
  font-size:17px; line-height:1; padding:3px 4px; align-self:start}
.f-fermer:hover{color:var(--ink)}

.f-corps{padding:12px 15px 6px; max-height:min(54vh, 470px); overflow-y:auto}
.jeton{display:inline-block; font-size:10px; padding:2px 7px; border-radius:99px; margin:0 4px 7px 0; font-weight:600; letter-spacing:.2px}
.j-fr{background:var(--fr-bg); color:var(--fr)}
.j-nf{background:var(--nf-bg); color:var(--nf)}
.j-or{background:var(--or-bg); color:var(--or)}
.j-al{background:var(--alerte-bg); color:var(--alerte)}

.f-faits{display:grid; grid-template-columns:62px 1fr; gap:6px 10px; font-size:12.7px; line-height:1.42; margin:2px 0 0}
.f-faits dt{color:var(--faint); font-size:9.6px; text-transform:uppercase; letter-spacing:.6px;
  font-weight:700; padding-top:2.5px}
.f-faits dd{margin:0}
.f-marquants{margin:11px 0 2px; padding:0; list-style:none; border-top:1px solid var(--line-soft); padding-top:10px}
.f-marquants li{position:relative; padding-left:15px; font-size:12.7px; line-height:1.46; margin-bottom:8px}
.f-marquants li::before{content:""; position:absolute; left:0; top:6px; width:6px; height:6px;
  border-radius:50%; background:var(--or)}
.f-note{font-size:11.9px; color:var(--ink); background:var(--alerte-bg);
  border-left:3px solid var(--alerte); border-radius:0 6px 6px 0;
  padding:8px 11px; margin:10px 0 0; line-height:1.45}
.f-note b{display:block; color:var(--alerte); font-size:9.6px; text-transform:uppercase;
  letter-spacing:.7px; margin-bottom:3px}
.f-corps > .f-note:first-of-type{margin-top:12px; padding-top:8px}
.f-bas{padding:10px 15px 12px; border-top:1px solid var(--line-soft);
  display:flex; align-items:center; gap:10px; background:var(--surface)}
.f-modifiable{cursor:pointer; transition:filter .12s, box-shadow .12s}
.f-modifiable:hover{filter:brightness(.82); box-shadow:0 0 0 3px var(--or)}
#avis-arbre{position:fixed; left:50%; bottom:22px; transform:translate(-50%,16px); opacity:0;
  pointer-events:none; transition:opacity .18s, transform .18s; z-index:80;
  background:var(--ink); color:var(--bg); padding:10px 16px; border-radius:9px; font-size:14px;
  max-width:min(560px, calc(100vw - 32px))}
#avis-arbre.visible{opacity:1; transform:translate(-50%,0)}
#avis-arbre.erreur{background:var(--alerte); color:#fff}
.f-plus{font-size:12.7px; font-weight:600; color:var(--or); text-decoration:none;
  display:inline-flex; align-items:center; gap:5px}
.f-plus:hover{text-decoration:underline; text-underline-offset:2px}
.f-plus::after{content:"→"}
.f-compte{margin-left:auto; font-size:10.6px; color:var(--faint)}
.lien-pers{color:var(--or); cursor:pointer; text-decoration:underline; text-underline-offset:2px}
.lieu{color:var(--or); text-decoration:underline dotted;
  text-decoration-color:color-mix(in srgb, var(--or) 50%, transparent);
  text-underline-offset:2.5px}
.lieu::after{content:""; display:inline-block; width:.66em; height:.66em; margin-left:.2em;
  vertical-align:-.02em; background-color:currentColor; opacity:.75;
  -webkit-mask:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%3E%3Cpath%20d%3D%22M12%202a7%207%200%200%200-7%207c0%205.3%207%2013%207%2013s7-7.7%207-13a7%207%200%200%200-7-7zm0%209.6A2.6%202.6%200%201%201%2012%206.4a2.6%202.6%200%200%201%200%205.2z%22%2F%3E%3C%2Fsvg%3E") center/contain no-repeat; mask:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%3E%3Cpath%20d%3D%22M12%202a7%207%200%200%200-7%207c0%205.3%207%2013%207%2013s7-7.7%207-13a7%207%200%200%200-7-7zm0%209.6A2.6%202.6%200%201%201%2012%206.4a2.6%202.6%200%200%201%200%205.2z%22%2F%3E%3C%2Fsvg%3E") center/contain no-repeat}
.lieu:hover{text-decoration-style:solid; text-decoration-color:var(--or)}
.lieu:hover::after{opacity:1}
.marque-cert{font-size:9.6px; font-weight:700; padding:1px 5px; border-radius:4px; margin-left:5px; letter-spacing:.2px}
.c-approximative{background:var(--surface-2); color:var(--muted)}
.c-deduite{background:var(--fr-bg); color:var(--fr)}
.c-divergente,.c-incoherente,.c-inconnue{background:var(--alerte-bg); color:var(--alerte)}

/* ---------- panneau des problèmes ---------- */
#problemes{
  position:fixed; top:60px; left:0; bottom:0; width:430px; max-width:92vw; z-index:46;
  background:var(--surface); border-right:1px solid var(--line-soft); box-shadow:var(--ombre);
  overflow-y:auto; padding:20px 22px 44px; transform:translateX(-100%);
  transition:transform .2s ease; visibility:hidden;
}
#problemes.ouvert{transform:none; visibility:visible}
#problemes h2{margin:0 0 4px; font-size:19px; font-weight:600}
#problemes > p{margin:0 0 16px; font-size:12.8px; color:var(--muted); line-height:1.5}
.pb{border:1px solid var(--line-soft); border-radius:8px; padding:12px 14px; margin-bottom:11px; background:var(--bg)}
.pb-tete{display:flex; align-items:baseline; gap:8px; margin-bottom:6px; flex-wrap:wrap}
.pb-type{font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.7px; padding:2px 7px; border-radius:4px}
.g-forte{background:var(--alerte-bg); color:var(--alerte)}
.g-moyenne{background:var(--or-bg); color:var(--or)}
.g-faible{background:var(--surface-2); color:var(--muted)}
.pb-pages{font-size:11px; color:var(--faint); font-variant-numeric:tabular-nums}
.pb p{margin:0; font-size:13px; line-height:1.52}

/* ---------- légende ---------- */
.legende{
  position:fixed; left:14px; bottom:14px; z-index:30;
  background:color-mix(in srgb, var(--surface) 93%, transparent); backdrop-filter:blur(8px);
  border:1px solid var(--line-soft); border-radius:var(--r); padding:9px 13px;
  font-size:11.3px; color:var(--muted); line-height:1.75; box-shadow:var(--ombre); max-width:238px;
}
.legende summary{
  list-style:none; cursor:pointer; color:var(--ink); font-size:10.5px; text-transform:uppercase;
  letter-spacing:.8px; font-weight:700; user-select:none;
}
.legende summary::-webkit-details-marker{display:none}
.legende summary::after{content:" +"; color:var(--faint)}
.legende[open] summary::after{content:" –"}
.legende[open] summary{margin-bottom:6px}
.legende i{display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:7px; vertical-align:-1px; border:2.5px solid}
.legende .tr{display:inline-block; width:12px; height:0; border-top:2.5px solid var(--or); margin-right:7px; vertical-align:4px}
.legende .tir{display:inline-block; width:12px; height:0; border-top:1.5px dashed var(--line); margin-right:7px; vertical-align:4px}
.aide{position:fixed; right:14px; bottom:14px; z-index:30; font-size:11.3px; color:var(--faint);
  background:color-mix(in srgb, var(--surface) 90%, transparent); backdrop-filter:blur(8px);
  border:1px solid var(--line-soft); border-radius:var(--r); padding:8px 12px;}

@media (max-width:980px){
  .plaque span{display:none}
  .recherche input{width:118px}
  .legende{display:none}
  .aide{display:none}
  .compteur{display:none}
}
</style>
</head>
<body>

<header>
  <div class="plaque"><b>__TITRE__</b><span>__SOUS_TITRE__</span></div>
  <div class="espace"></div>
  <div class="outils">
    <div class="bascule">
      <button id="m-portraits" aria-pressed="true">Portraits</button>
      <button id="m-fiches" aria-pressed="false">Cartes</button>
    </div>
    <div class="recherche" id="boite-rech">
      <input id="rech" type="search" placeholder="Chercher un nom…" autocomplete="off" spellcheck="false">
      <button class="effacer" id="effacer" title="Effacer">&times;</button>
    </div>
    <span class="compteur" id="compteur"></span>
    <button class="btn" id="b-lignee" aria-pressed="false" title="Mettre en évidence la lignée directe">Lignée directe</button>
    <button class="btn" id="b-pb" aria-pressed="false" title="Divergences et lacunes du document source">Problèmes <span id="n-pb"></span></button>
    <button class="btn rond" id="b-moins" title="Dézoomer">&minus;</button>
    <button class="btn rond" id="b-plus" title="Zoomer">+</button>
    <button class="btn" id="b-replier" title="Ne garder que les deux premières générations">Replier</button>
    <button class="btn" id="b-reset" title="Tout revoir">Recadrer</button>
    <button class="btn rond" id="b-theme" title="Clair / sombre">◐</button>
  </div>
</header>

<div id="toile"><svg id="svg"><defs id="defs"></defs><g id="monde"></g></svg></div>

<div id="fiche"></div>

<div id="problemes">
  <h2>Ce que le document ne tranche pas</h2>
  <p>Divergences internes, dates invraisemblables et chaînons manquants relevés dans la source. Rien n'a été corrigé d'office : à vous de trancher sur pièces.</p>
  <div id="liste-pb"></div>
</div>

<details class="legende">
  <summary>Légende</summary>
  <div><i style="border-color:var(--fr)"></i>Resté en France</div>
  <div><i style="border-color:var(--nf)"></i>Passé en Nouvelle-France</div>
  <div><i style="border-color:var(--or)"></i>Lignée directe</div>
  <div><span class="tir"></span>Rattachement non documenté</div>
  <div><i style="border-color:var(--alerte)"></i>Donnée contestée</div>
</details>
<div class="aide">Glisser pour déplacer · molette pour zoomer · cliquer un portrait</div>

<script>
"use strict";
const D = __DONNEES__;

/* ======================= graphe ======================= */
const P = D.personnes, U = D.unions;
const unionsDe = {}, unionParente = {};
U.forEach(u=>{
  u.conjoints.forEach(c=>{ (unionsDe[c] = unionsDe[c] || []).push(u); });
  (u.enfants||[]).forEach(e=>{ unionParente[e] = u; });
});

function construire(idPivot, vu){
  vu = vu || new Set();
  if(vu.has(idPivot)) return null;
  vu.add(idPivot);
  const conjoints = [], groupes = [];
  (unionsDe[idPivot]||[]).forEach(u=>{
    const autre = u.conjoints.find(c=>c!==idPivot);
    if(autre){ if(!vu.has(autre)) vu.add(autre); conjoints.push({id:autre, union:u}); }
    groupes.push({union:u, enfants:(u.enfants||[]).map(e=>construire(e,vu)).filter(Boolean)});
  });
  return { id:idPivot, conjoints, groupes,
           enfants: groupes.reduce((a,g)=>a.concat(g.enfants),[]) };
}
/* ---------------- parcours vers le haut ----------------
   Miroir de construire(). Là où l'autre prend les enfants d'une union,
   celui-ci prend les conjoints de l'union PARENTE. L'index unionParente
   était déjà construit plus haut depuis le premier jour : le lien de
   filiation existait dans les deux sens, personne ne l'avait jamais
   remonté.

   C'est ce parcours qui relie les deux lignées. Un moteur qui ne sait que
   descendre atteint Sébastien par les Jean ET par les Trịnh, et le dessine
   deux fois — chaque racine ayant son propre ensemble « vu ». En montant
   depuis une seule personne, chacun n'est atteint qu'une fois, et les deux
   familles se rejoignent d'elles-mêmes à l'endroit où elles se sont
   effectivement rencontrées. */
function construireHaut(id, vu, branche){
  vu = vu || new Set();
  if(vu.has(id)) return null;
  vu.add(id);
  const u = unionParente[id];
  const parents = (u ? u.conjoints : []).filter(c=>!vu.has(c));
  const noeud = { id, conjoints: [], groupes: [], enfants: [], branche };
  if(branche) BRANCHE_PERS[id] = branche;
  /* La fratrie. Un arbre ascendant ne montre que des ancêtres, et les
     frères et soeurs n'en sont pas : sans ce relevé, Vincent, les oncles
     Trịnh et les onze frères et soeurs de Fernande sont dans les données
     et invisibles à l'écran. On les pose à côté, dans la même rangée, sans
     leur descendance — c'est une fratrie qu'on veut voir, pas un deuxième
     arbre. */
  if(u && (u.enfants||[]).length > 1){
    noeud.fratrie = u.enfants.filter(e => e !== id && P[e]);
    noeud.rang = u.enfants.indexOf(id);
  }
  if(u && parents.length){
    const sous = parents.map(p=>construireHaut(p, vu, BRANCHE_DE[p] || branche))
                        .filter(Boolean);
    if(sous.length){
      noeud.groupes.push({union:u, enfants:sous});
      noeud.enfants = sous;
    }
  }
  return noeud;
}

/* Quelle branche pour qui : déclaré dans meta.branches, jamais deviné. La
   branche se propage ensuite vers le haut, de tête en ancêtre. */
const BRANCHE_DE = {};
((D.meta&&D.meta.branches)||[]).forEach(b=>{ BRANCHE_DE[b.tete] = b.id; });

const BRANCHE_PERS = {};
const BRANCHE_NOM = {};
((D.meta&&D.meta.branches)||[]).forEach(b=>{ BRANCHE_NOM[b.id] = b.titre || b.id; });
const MONTANT = !!(D.meta && D.meta.pivot && P[D.meta.pivot]);
const racines = [];
if(MONTANT){
  racines.push(construireHaut(D.meta.pivot, null, null));
}else{
  (D.racines||[]).forEach(rid=>{ const u = U.find(x=>x.id===rid); if(u) racines.push(construire(u.conjoints[0])); });
  (D.detaches||[]).forEach(pid=>{ racines.push(construire(pid)); });
}
const principal = racines[0];
const detaches = racines.slice(1);

/* ---------------- dépliage ----------------
   À 60 personnes on dessinait tout. À 260, la disposition fait 30 000 px de
   large et aucun zoom ne la rend lisible — c'est le même mur qu'au premier
   jour, à l'échelle du livre entier.

   Un noeud fermé se comporte exactement comme une feuille : la disposition
   étant récursive, il suffit de lui cacher ses enfants pour que toute la
   largeur en aval disparaisse. On ne change donc pas l'algorithme, on change
   ce qu'il voit. */
/* Deux générations ouvertes quand il n'y a qu'un arbre.

   Pour une forêt : TOUT REPLIÉ. À 206 familles, ouvrir ne serait-ce qu'un
   niveau dessine quatre mille médaillons — mesuré — et c'est le même mur
   qu'avant, déplacé. Entièrement replié, chaque famille se réduit à son
   couple de tête et à son compte : la page d'ouverture devient l'index des
   familles, et l'index est le même objet que l'arbre. Un clic ouvre celle
   qu'on veut. */
/* Combien de générations ouvertes d'emblée. En montant, c'est le nombre de
   crans au-dessus du pivot qu'on veut voir sans rien cliquer : meta.profondeur_ouverte.
   Par défaut 3 — l'enfant, ses parents, ses grands-parents. */
const PROFONDEUR_INITIALE = MONTANT
  ? ((D.meta && D.meta.profondeur_ouverte) || 3)
  : (racines.length > 3 ? 0 : 2);

function preparer(n, prof){
  n.total = 0;
  (n.enfants||[]).forEach(e=>{ n.total += 1 + preparer(e, prof+1); });
  n.prof = prof;
  n.ouvert = prof < PROFONDEUR_INITIALE;
  return n.total;
}
[principal].concat(detaches).filter(Boolean).forEach(n=>preparer(n,0));

/* Les deux seules portes par lesquelles la disposition et le dessin
   atteignent la descendance. Tout passe par là, donc rien ne peut oublier
   l'état d'ouverture. */
function enf(n){ return n.ouvert ? (n.enfants||[]) : []; }
function grp(n){ return n.ouvert ? (n.groupes||[]) : []; }

const indexNoeuds = {};
function recenser(n){ indexNoeuds[n.id]=n; (n.enfants||[]).forEach(recenser); }
[principal].concat(detaches).filter(Boolean).forEach(recenser);

function basculer(id){
  const n = indexNoeuds[id];
  if(!n || !(n.enfants||[]).length) return;
  n.ouvert = !n.ouvert;
  rendre(true);
}

/* Ouvre tout le chemin de la racine jusqu'à une personne. Sans cela, la
   recherche ne trouve rien de ce qui est replié, et l'utilisateur conclut
   que la personne n'est pas dans l'arbre. */
function ouvrirChemin(id){
  let n = indexNoeuds[id];
  if(!n) return false;
  const chemin = [];
  while(n){ chemin.push(n); n = n.parent; }
  chemin.forEach(x=>{ if((x.enfants||[]).length) x.ouvert = true; });
  return true;
}
function poserParents(n){ (n.enfants||[]).forEach(e=>{ e.parent = n; poserParents(e); }); }
[principal].concat(detaches).filter(Boolean).forEach(poserParents);

function replierTout(){
  Object.values(indexNoeuds).forEach(n=>{ n.ouvert = n.prof < PROFONDEUR_INITIALE; });
  rendre(false);
}
const ancNode = (function t(n){ if(P[n.id]&&P[n.id].ancetre) return n;
  for(const e of (n.enfants||[])){ const r=t(e); if(r) return r; } return null; })(principal);

/* ======================= dimensions ======================= */
/* portraits : de haut en bas, médaillons ronds */
const RAYON=34, MED_L=118, MED_H=118, MED_EP=18, MED_EF=22, MED_NIV=168;
/* +1 : les enfants sous les parents. -1 : les parents au-dessus de l'enfant.
   La disposition est la même ; seul le signe de l'axe change. */
const SENS = MONTANT ? -1 : 1;
/* fiches : de gauche à droite, cartes */
const FIC_L=184, FIC_H=62, FIC_EP=8, FIC_EF=16, FIC_COL=282;

let mode = "portraits";

/* ======================= mise en page ======================= */
function poserPuces(n){
  /* Un noeud montant est UNE personne. Les deux parents sont deux noeuds
     frères et non deux puces d'un même noeud : c'est ce qui permet de
     remonter séparément dans chacune des deux familles. */
  if(!n.puces) n.puces = [{id:n.id}];
  (n.enfants||[]).forEach(poserPuces);
}
if(MONTANT) racines.filter(Boolean).forEach(poserPuces);

function taillePuces(n, pas, ecart){
  const k = 1 + n.conjoints.length + ((n.fratrie||[]).length);
  return k*pas + (k-1)*ecart;
}

/* La rangée d'un noeud, dans l'ordre : la fratrie telle que la source
   l'énumère — donc par ordre de naissance — puis les conjoints. La personne
   de la lignée garde sa place parmi ses frères et soeurs ; la sortir pour la
   mettre en tête mentirait sur son rang. */
function rangee(n){
  const f = n.fratrie || [];
  const ordre = [];
  if(f.length){
    const rang = Math.max(0, Math.min(n.rang === undefined ? 0 : n.rang, f.length));
    for(let i = 0; i < f.length; i++){
      if(i === rang) ordre.push({id:n.id, focal:true});
      ordre.push({id:f[i], fratrie:true});
    }
    if(rang >= f.length) ordre.push({id:n.id, focal:true});
  }else{
    ordre.push({id:n.id, focal:true});
  }
  n.conjoints.forEach(c => ordre.push({id:c.id, union:c.union}));
  return ordre;
}

/* -- portraits : l'axe principal est horizontal, les générations descendent -- */
function mesurerV(n){
  const lp = taillePuces(n, MED_L, MED_EP);
  if(!enf(n).length){ n.taille = lp; n.tailleEnfants = 0; return n.taille; }
  let s = 0; enf(n).forEach((e,i)=>{ s += mesurerV(e); if(i) s += MED_EF; });
  n.tailleEnfants = s; n.taille = Math.max(lp, s); return n.taille;
}
function placerV(n, gauche, y){
  n.y = y;
  const lp = taillePuces(n, MED_L, MED_EP);
  if(!enf(n).length){ n.debut = gauche + (n.taille-lp)/2; }
  else{
    let cx = gauche + (n.taille - n.tailleEnfants)/2;
    enf(n).forEach((e,i)=>{ if(i) cx += MED_EF; placerV(e, cx, y+SENS*MED_NIV); cx += e.taille; });
    const a=enf(n)[0], b=enf(n)[enf(n).length-1];
    const c=(a.pivot+b.pivot)/2;
    n.debut = Math.min(Math.max(c-lp/2, gauche), gauche+n.taille-lp);
  }
  n.puces = rangee(n).map((e,i)=>Object.assign({}, e,
      {x:n.debut + i*(MED_L+MED_EP), y:y}));
  const moi = n.puces.find(p=>p.focal) || n.puces[0];
  /* Le trait vers les parents part de la personne de la lignée, pas du
     milieu de la rangée : sinon il viserait un frère. */
  n.pivot = moi.x + MED_L/2;
  n.centre = n.debut + lp/2;
}

/* -- fiches : l'axe principal est vertical, les générations vont vers la droite -- */
function mesurerH(n){
  const hp = taillePuces(n, FIC_H, FIC_EP);
  if(!enf(n).length){ n.taille = hp; n.tailleEnfants = 0; return n.taille; }
  let s = 0; enf(n).forEach((e,i)=>{ s += mesurerH(e); if(i) s += FIC_EF; });
  n.tailleEnfants = s; n.taille = Math.max(hp, s); return n.taille;
}
function placerH(n, haut, x){
  n.x = x;
  const hp = taillePuces(n, FIC_H, FIC_EP);
  if(!enf(n).length){ n.debut = haut + (n.taille-hp)/2; }
  else{
    let cy = haut + (n.taille - n.tailleEnfants)/2;
    enf(n).forEach((e,i)=>{ if(i) cy += FIC_EF; placerH(e, cy, x+FIC_COL); cy += e.taille; });
    const a=enf(n)[0], b=enf(n)[enf(n).length-1];
    const c=(a.pivot+b.pivot)/2;
    n.debut = Math.min(Math.max(c-hp/2, haut), haut+n.taille-hp);
  }
  n.puces = rangee(n).map((e,i)=>Object.assign({}, e,
      {x:x, y:n.debut + i*(FIC_H+FIC_EP)}));
  const moiH = n.puces.find(p=>p.focal) || n.puces[0];
  n.pivot = moiH.y + FIC_H/2;
  n.centre = n.debut + hp/2;
}

/* Hauteur réellement occupée par un arbre déplié : le nombre de niveaux
   ouverts, pas le nombre de générations existantes. */
function niveauxOuverts(n){
  if(!n.ouvert || !(n.enfants||[]).length) return 1;
  let m = 0;
  enf(n).forEach(e=>{ m = Math.max(m, niveauxOuverts(e)); });
  return 1 + m;
}

function disposer(){
  if(mode==="portraits"){
    mesurerV(principal); placerV(principal, 0, 0);
    if(ancNode && detaches.length === 1){
      /* Le cas d'origine : un seul nœud détaché, rattaché sous l'ancêtre
         par un trait pointillé — les générations manquantes de l'extrait. */
      const d = detaches[0]; mesurerV(d);
      placerV(d, ancNode.pivot - d.taille/2, ancNode.y + Math.round(MED_NIV*1.55));
    }else{
      /* Une forêt. Les empiler EN COLONNE, chacun sous le précédent.
         Auparavant ils étaient tous placés au même point : deux cents arbres
         superposés, illisibles, et rien ne le signalait — la page s'affichait
         sans erreur. Une colonne se parcourt ; une superposition, non. */
      let y = niveauxOuverts(principal) * MED_NIV + 140;
      detaches.forEach(d=>{
        mesurerV(d); placerV(d, 0, y);
        y += niveauxOuverts(d) * MED_NIV + 90;
      });
    }
  }else{
    mesurerH(principal); placerH(principal, 0, 0);
    if(ancNode && detaches.length === 1){
      const d = detaches[0]; mesurerH(d);
      placerH(d, ancNode.pivot - d.taille/2, ancNode.x + Math.round(FIC_COL*1.75));
    }else{
      let y = principal.taille + 90;
      detaches.forEach(d=>{ mesurerH(d); placerH(d, y, 0); y += d.taille + 70; });
    }
  }
}

/* ======================= rendu ======================= */
const NS="http://www.w3.org/2000/svg";
const monde=document.getElementById("monde"), defs=document.getElementById("defs");
function el(t,a){ const e=document.createElementNS(NS,t); for(const k in a) e.setAttribute(k,a[k]); return e; }

function anneeDe(f){ if(!f) return null;
  if(typeof f.tri==="number") return f.tri;
  const m=(f.texte||"").match(/(1[5-9]\d{2})/); return m?+m[1]:null; }
function vie(p){
  /* le « ~ » suit la date affichée, pas sa voisine (C-021) */
  const fn=anneeDe(p.naissance)?p.naissance:p.bapteme, fd=anneeDe(p.deces)?p.deces:p.sepulture;
  const n=anneeDe(fn), d=anneeDe(fd);
  const ap=f=>f&&(f.certitude==="approximative"||f.certitude==="deduite");
  const g=ap(fn)?"~":"", h=ap(fd)?"~":"";
  if(n&&d) return g+n+" – "+h+d;
  if(n) return g+n+" –"; if(d) return "– "+h+d; return "";
}
/* « nom_affiche » l'emporte quand il existe. En vietnamien le nom de
   famille précède le prénom : Trần Thị Tịch, et non « Thị Tịch Trần ».
   Imposer l'ordre occidental à un nom vietnamien le rend méconnaissable
   pour ceux à qui on l'enverra. */
function nomComplet(p){
  return (p.nom_affiche || ((p.prenom||"")+" "+(p.nom||""))).trim();
}
function initiales(p){
  /* Ne garder que des lettres. « Jos (Joseph) Pitre » donnait « J( » :
     la parenthèse comptait comme initiale du nom. */
  const lettre = s => { const m=(s||"").match(/[A-Za-zÀ-ÿ]/); return m?m[0]:""; };
  const a = lettre(p.prenom) || "?";
  const b = lettre((p.nom||"").replace(/^\(?[^)]*\)\s*/,"")) ||
            lettre((p.nom_affiche||"").split(/\s+/).slice(-1)[0]);
  return (a+(b||"")).toUpperCase();
}
function aProbleme(p){
  if(p.lacune) return true;
  return ["naissance","bapteme","deces","sepulture"].some(k=>{
    const f=p[k]; return f && (f.certitude==="divergente"||f.certitude==="incoherente"); });
}
function couper(txt, maxCar, maxLignes){
  const mots = txt.split(/[\s]+/); const lignes=[]; let cur="";
  mots.forEach(m=>{
    if(!cur) cur=m;
    else if((cur+" "+m).length<=maxCar) cur+=" "+m;
    else { lignes.push(cur); cur=m; }
  });
  if(cur) lignes.push(cur);
  if(lignes.length>maxLignes){
    const g=lignes.slice(0,maxLignes); g[maxLignes-1]=g[maxLignes-1].slice(0,maxCar-1)+"…"; return g;
  }
  return lignes;
}

let couchLiens, couchPuces, indexPuces={};

/* La classe d'un médaillon. Quand une branche est déclarée, c'est elle qui
   donne la couleur ; « pays » — resté en France / passé en Nouvelle-France —
   ne sert plus qu'aux arbres d'une seule origine. Ce vocabulaire-là ne veut
   rien dire pour une aïeule née à Saïgon : la fiche de Diên Thị Trần
   affichait « France », simplement parce que le champ manquait et que le
   défaut tombait sur « fr ». */
function classePuce(p, directe, detache, branche){
  const base = branche ? ("br-" + branche) : (p.pays || "fr");
  return "puce " + base + (directe ? " directe" : "")
       + (p.ancetre ? " ancetre" : "")
       + (detache && !MONTANT ? " detache" : "");
}

function puceMedaillon(id,x,y,directe,detache,branche){
  const p=P[id]; if(!p) return;
  const g=el("g",{class:classePuce(p,directe,detache,branche),
                  transform:`translate(${x},${y})`,"data-id":id});
  const cx=MED_L/2, cy=RAYON+4;
  if(p._photo){
    const cid="cl-"+id;
    if(!document.getElementById(cid)){
      const cp=el("clipPath",{id:cid});
      cp.appendChild(el("circle",{cx:0,cy:0,r:RAYON-1}));
      defs.appendChild(cp);
    }
    const w=el("g",{transform:`translate(${cx},${cy})`});
    w.appendChild(el("image",{href:p._photo, x:-(RAYON-1), y:-(RAYON-1),
      width:(RAYON-1)*2, height:(RAYON-1)*2, preserveAspectRatio:"xMidYMid slice",
      "clip-path":`url(#${cid})`}));
    g.appendChild(w);
  }else{
    g.appendChild(el("circle",{class:"disque", cx, cy, r:RAYON-1}));
    const t=el("text",{class:"monogramme", x:cx, y:cy+7.5, "text-anchor":"middle"});
    t.textContent=initiales(p); g.appendChild(t);
  }
  if(directe) g.appendChild(el("circle",{class:"halo", cx, cy, r:RAYON+5}));
  g.appendChild(el("circle",{class:"anneau", cx, cy, r:RAYON}));
  if(aProbleme(p)){
    g.appendChild(el("circle",{class:"pastille-fond", cx:cx+RAYON-7, cy:cy-RAYON+9, r:8}));
    const b=el("text",{class:"pastille", x:cx+RAYON-7, y:cy-RAYON+12.5, "text-anchor":"middle"});
    b.textContent="!"; g.appendChild(b);
  }
  let yy = cy+RAYON+15;
  couper(nomComplet(p), 19, 2).forEach(l=>{
    const t=el("text",{class:"nom", x:cx, y:yy, "text-anchor":"middle"}); t.textContent=l;
    g.appendChild(t); yy+=13;
  });
  const v=vie(p);
  if(v){ const t=el("text",{class:"vie", x:cx, y:yy-1, "text-anchor":"middle"}); t.textContent=v; g.appendChild(t); }
  g.addEventListener("click",ev=>{ev.stopPropagation();
    if(aBouge){ aBouge=false; return; }
    ouvrirFiche(id);});
  couchPuces.appendChild(g); indexPuces[id]=g;
}

function puceFiche(id,x,y,directe,detache,branche){
  const p=P[id]; if(!p) return;
  const g=el("g",{class:classePuce(p,directe,detache,branche),
                  transform:`translate(${x},${y})`,"data-id":id});
  g.appendChild(el("rect",{class:"cadre",x:0,y:0,width:FIC_L,height:FIC_H}));
  g.appendChild(el("rect",{class:"bande",x:0,y:9,width:3.5,height:FIC_H-18}));
  let dx = 13;
  if(p._photo){
    const cid="clf-"+id;
    if(!document.getElementById(cid)){
      const cp=el("clipPath",{id:cid}); cp.appendChild(el("circle",{cx:0,cy:0,r:19}));
      defs.appendChild(cp);
    }
    const w=el("g",{transform:`translate(${34},${FIC_H/2})`});
    w.appendChild(el("image",{href:p._photo,x:-19,y:-19,width:38,height:38,
      preserveAspectRatio:"xMidYMid slice","clip-path":`url(#${cid})`}));
    w.appendChild(el("circle",{class:"anneau",cx:0,cy:0,r:19,"stroke-width":2}));
    g.appendChild(w); dx = 62;
  }
  const t1=el("text",{class:"nomf",x:dx,y:23}); t1.textContent=nomComplet(p); g.appendChild(t1);
  const v=vie(p);
  if(v){ const t2=el("text",{class:"vief",x:dx,y:39}); t2.textContent=v; g.appendChild(t2); }
  const bas=p.surnom||(p.metiers&&p.metiers[0])||(p.lieux&&p.lieux[0])||"";
  if(bas){ const t3=el("text",{class:"rang",x:dx,y:v?53:40});
    t3.textContent = bas.length>24?bas.slice(0,23)+"…":bas; g.appendChild(t3); }
  if(aProbleme(p)){
    g.appendChild(el("circle",{class:"pastille-fond",cx:FIC_L-14,cy:15,r:8}));
    const b=el("text",{class:"pastille",x:FIC_L-14,y:18.5,"text-anchor":"middle"}); b.textContent="!";
    g.appendChild(b);
  }
  g.addEventListener("click",ev=>{ev.stopPropagation();
    if(aBouge){ aBouge=false; return; }
    ouvrirFiche(id);});
  couchPuces.appendChild(g); indexPuces[id]=g;
}

/* Le bouton de dépliage. Il a sa propre cible de clic, séparée du
   médaillon : le clic sur un médaillon ouvre la fiche, et mêler les deux
   gestes sur la même forme rendrait les deux imprévisibles. */
function bouton(n, cx, cy){
  if(!(n.enfants||[]).length) return;
  const ferme = !n.ouvert;
  const texte = ferme ? ("+"+n.total) : "−";
  const larg = Math.max(22, 11 + texte.length*7.2);
  const g = el("g",{class:"plier"+(ferme?" ferme":""),"data-noeud":n.id,
                    transform:`translate(${cx-larg/2},${cy})`});
  g.appendChild(el("rect",{x:0,y:0,width:larg,height:16,rx:8}));
  const tx = el("text",{x:larg/2,y:11.5,"text-anchor":"middle"});
  tx.textContent = texte; g.appendChild(tx);
  g.addEventListener("click", ev=>{ ev.stopPropagation(); basculer(n.id); });
  couchPuces.appendChild(g);
  return g;
}

function dessinerV(n, detache){
  n.puces.forEach((pu,i)=>{
    puceMedaillon(pu.id, pu.x, pu.y, !!(P[pu.id]&&P[pu.id].lignee), detache, n.branche);
    if(i>0 && pu.union){
      const u=pu.union, d=!!u.lignee;
      const ym=pu.y+RAYON+4;
      const x1=n.puces[i-1].x+MED_L/2+RAYON, x2=pu.x+MED_L/2-RAYON;
      couchLiens.appendChild(el("path",{class:"alliance"+(d?" directe":""), d:`M ${x1} ${ym} H ${x2}`}));
      const lab=(u.mariage&&u.mariage.texte)?u.mariage.texte.match(/(1[5-9]\d{2})/):null;
      if(lab){ const t=el("text",{class:"etiq-mariage",x:(x1+x2)/2,y:ym-7,"text-anchor":"middle"});
        t.textContent=lab[1]; couchLiens.appendChild(t); }
    }
  });
  if(n.total) bouton(n, n.pivot, SENS>0 ? n.y+MED_H+10 : n.y-26);
  grp(n).forEach((gr,gi)=>{
    if(!gr.enfants.length) return;
    const idx=n.puces.findIndex(pu=>pu.union===gr.union);
    const xa=n.pivot, xb=idx>0?n.puces[idx].x+MED_L/2:xa;
    const xU=(xa+xb)/2;
    const yDep = SENS>0 ? n.y+MED_H+4  : n.y-4;
    const yBus = SENS>0 ? n.y+MED_H+26+gi*10 : n.y-26-gi*10;
    const d=!!gr.union.lignee, cls="lien"+(d?" directe":"");
    couchLiens.appendChild(el("path",{class:cls,d:`M ${xU} ${yDep} V ${yBus}`}));
    const xs=gr.enfants.map(e=>e.pivot);
    couchLiens.appendChild(el("path",{class:cls,d:`M ${Math.min(xU,...xs)} ${yBus} H ${Math.max(xU,...xs)}`}));
    gr.enfants.forEach(e=>{
      const de=!!(P[e.id]&&P[e.id].lignee)&&d;
      couchLiens.appendChild(el("path",{class:"lien"+(de?" directe":""),
        d:`M ${e.pivot} ${yBus} V ${SENS>0 ? e.y+4 : e.y+MED_H-4}`}));
      dessinerV(e, detache);
    });
  });
}

function dessinerH(n, detache){
  n.puces.forEach((pu,i)=>{
    puceFiche(pu.id, pu.x, pu.y, !!(P[pu.id]&&P[pu.id].lignee), detache, n.branche);
    if(i>0 && pu.union){
      const u=pu.union, d=!!u.lignee, xm=n.x+24;
      const y1=n.puces[i-1].y+FIC_H, y2=pu.y;
      couchLiens.appendChild(el("path",{class:"alliance"+(d?" directe":""),d:`M ${xm} ${y1} V ${y2}`}));
      const lab=(u.mariage&&u.mariage.texte)?u.mariage.texte.match(/(1[5-9]\d{2})/):null;
      if(lab){ const t=el("text",{class:"etiq-mariage",x:xm+7,y:(y1+y2)/2+3.5});
        t.textContent=lab[1]; couchLiens.appendChild(t); }
    }
  });
  if(n.total) bouton(n, n.x+FIC_L+13, n.debut+FIC_H/2);
  grp(n).forEach((gr,gi)=>{
    if(!gr.enfants.length) return;
    const idx=n.puces.findIndex(pu=>pu.union===gr.union);
    const ya=n.debut+FIC_H/2, yb=idx>0?n.puces[idx].y+FIC_H/2:ya;
    const yU=(ya+yb)/2, xDep=n.x+FIC_L, xBus=n.x+FIC_COL-54+gi*11;
    const d=!!gr.union.lignee, cls="lien"+(d?" directe":"");
    couchLiens.appendChild(el("path",{class:cls,d:`M ${xDep} ${yU} H ${xBus}`}));
    const ys=gr.enfants.map(e=>e.pivot);
    couchLiens.appendChild(el("path",{class:cls,d:`M ${xBus} ${Math.min(yU,...ys)} V ${Math.max(yU,...ys)}`}));
    gr.enfants.forEach(e=>{
      const de=!!(P[e.id]&&P[e.id].lignee)&&d;
      couchLiens.appendChild(el("path",{class:"lien"+(de?" directe":""),d:`M ${xBus} ${e.pivot} H ${e.x}`}));
      dessinerH(e, detache);
    });
  });
}

let enCoursDeRendu=false;
function redessine(garderVue){
  if(enCoursDeRendu) return;
  enCoursDeRendu=true; rendre(garderVue); enCoursDeRendu=false;
}
function rendre(garderVue){
  const vx=tx, vy=ty, ve=ech;
  monde.textContent=""; defs.textContent=""; indexPuces={};
  couchLiens=el("g",{}); couchPuces=el("g",{});
  monde.appendChild(couchLiens); monde.appendChild(couchPuces);
  disposer();
  if(mode==="portraits"){
    dessinerV(principal,false); detaches.forEach(d=>dessinerV(d,true));
    if(ancNode&&detaches.length){
      const d0=detaches[0], x=ancNode.pivot;
      couchLiens.insertBefore(el("path",{class:"lien","stroke-dasharray":"7 6",
        stroke:"var(--or)","stroke-width":"2",
        d:`M ${x} ${ancNode.y+MED_H+4} V ${d0.y}`}), couchLiens.firstChild);
      const t=el("text",{class:"ruban",x:x+14,y:(ancNode.y+MED_H+d0.y)/2+4});
      t.textContent="générations 4 et 5 — absentes de l'extrait"; couchLiens.appendChild(t);
    }
  }else{
    dessinerH(principal,false); detaches.forEach(d=>dessinerH(d,true));
    if(ancNode&&detaches.length){
      const d0=detaches[0], y=ancNode.pivot;
      couchLiens.insertBefore(el("path",{class:"lien","stroke-dasharray":"7 6",
        stroke:"var(--or)","stroke-width":"2",
        d:`M ${ancNode.x+FIC_L} ${y} H ${d0.x}`}), couchLiens.firstChild);
      const t=el("text",{class:"ruban",x:(ancNode.x+FIC_L+d0.x)/2,y:y-12,"text-anchor":"middle"});
      t.textContent="générations 4 et 5 — absentes de l'extrait"; couchLiens.appendChild(t);
    }
  }
  if(garderVue){ tx=vx; ty=vy; ech=ve; appliquer(); } else vueInitiale();
  if(!enCoursDeRendu) chercher();
  appliquerLignee();
  if(selection && indexPuces[selection]){
    indexPuces[selection].classList.add("selectionne");
    if(boiteFiche.classList.contains("ouverte")) positionnerFiche(selection);
  }
}

/* ======================= zoom & déplacement ======================= */
const toile=document.getElementById("toile");
let ech=1, tx=0, ty=0;
function appliquer(){ monde.setAttribute("transform",`translate(${tx},${ty}) scale(${ech})`); }
function recadrer(){
  const b=monde.getBBox(), r=toile.getBoundingClientRect();
  ech=Math.max(Math.min(Math.min((r.width-80)/b.width,(r.height-80)/b.height),1),.06);
  tx=(r.width-b.width*ech)/2-b.x*ech; ty=(r.height-b.height*ech)/2-b.y*ech; appliquer();
}
function vueInitiale(){
  const b=monde.getBBox(), r=toile.getBoundingClientRect();
  const tient=Math.min((r.width-80)/b.width,(r.height-80)/b.height);
  if(tient>=.8){ recadrer(); return; }
  ech=.82;
  /* Sur quoi la vue s'ouvre. Dans un arbre montant, c'est le pivot : la
     demande est que Samuel reste centré à chaque ouverture. ancNode ne
     convient que dans un arbre descendant, où il porte l'extrait rattaché.
     Et il faut qu'il ait VRAIMENT été placé : ancNode se cherche dans
     n.enfants au complet, alors que placerV ne descend que par enf(n), les
     niveaux ouverts. Un ancêtre replié n'a pas de pivot, et la vue entière
     partait alors sur translate(NaN) — l'arbre s'affichait sans erreur de
     script, décalé hors du cadre. */
  const place = x => x && Number.isFinite(mode==="portraits" ? x.pivot : x.x);
  const c = (!MONTANT && place(ancNode)) ? ancNode : principal;
  const cx = (mode==="portraits") ? c.pivot : c.x+FIC_L/2;
  const cy = (mode==="portraits") ? c.y+MED_H/2 : c.pivot;
  tx = (b.width*ech  <= r.width-70)  ? (r.width -b.width *ech)/2 - b.x*ech : r.width*0.40 - cx*ech;
  ty = (b.height*ech <= r.height-70) ? (r.height-b.height*ech)/2 - b.y*ech : r.height*0.46 - cy*ech;
  appliquer();
}
/* Déplacement : surtout PAS de setPointerCapture sur la toile — la capture
   détourne le clic vers la toile et les médaillons ne reçoivent plus rien.
   On suit le pointeur sur window, et on ne considère qu'il y a glissement
   qu'au-delà d'un petit seuil, pour qu'un clic reste un clic. */
let pret=false, glisse=false, aBouge=false, dx=0, dy=0, x0=0, y0=0;
const SEUIL=4;
toile.addEventListener("pointerdown",e=>{
  if(e.pointerType==="mouse" && e.button!==0) return;
  pret=true; glisse=false; aBouge=false;
  x0=e.clientX; y0=e.clientY; dx=e.clientX-tx; dy=e.clientY-ty;
});
window.addEventListener("pointermove",e=>{
  if(!pret) return;
  if(!glisse){
    if(Math.abs(e.clientX-x0)<SEUIL && Math.abs(e.clientY-y0)<SEUIL) return;
    glisse=true; aBouge=true; toile.classList.add("glisse");
    if(boiteFiche.classList.contains("ouverte")) fermerFiche();
  }
  tx=e.clientX-dx; ty=e.clientY-dy; appliquer();
});
function finGlisse(){ pret=false; glisse=false; toile.classList.remove("glisse"); }
window.addEventListener("pointerup", finGlisse);
window.addEventListener("pointercancel", finGlisse);
toile.addEventListener("wheel",e=>{
  e.preventDefault();
  const r=toile.getBoundingClientRect(), mx=e.clientX-r.left, my=e.clientY-r.top;
  const ne=Math.min(Math.max(ech*Math.exp(-e.deltaY*0.0014),.06),3.2);
  tx=mx-(mx-tx)*(ne/ech); ty=my-(my-ty)*(ne/ech); ech=ne; appliquer();
},{passive:false});
function zoomer(f){
  const r=toile.getBoundingClientRect(), mx=r.width/2, my=r.height/2;
  const ne=Math.min(Math.max(ech*f,.06),3.2);
  tx=mx-(mx-tx)*(ne/ech); ty=my-(my-ty)*(ne/ech); ech=ne; appliquer();
}
document.getElementById("b-plus").onclick=()=>zoomer(1.25);
document.getElementById("b-moins").onclick=()=>zoomer(.8);
document.getElementById("b-replier").onclick=replierTout;
document.getElementById("b-reset").onclick=recadrer;
toile.addEventListener("click",()=>{ if(!aBouge) fermerFiche(); aBouge=false; });

/* ======================= la fiche : carte flottante ======================= */
const boiteFiche=document.getElementById("fiche");
let selection=null;
/* la carte ne se referme pas quand on clique dedans */
boiteFiche.addEventListener("pointerdown",e=>e.stopPropagation());
boiteFiche.addEventListener("click",e=>e.stopPropagation());
function ech2(s){ return String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }
const LIB={approximative:"approx.",deduite:"déduit",divergente:"divergent",incoherente:"incohérent",inconnue:"inconnu"};
function cert(x){ return x&&x.certitude&&x.certitude!=="attestee"
  ? `<span class="marque-cert c-${x.certitude}">${LIB[x.certitude]||x.certitude}</span>` : ""; }

/* -- contenu de la carte -- */
function ouvrirFiche(id){
  const p=P[id]; if(!p) return;
  if(selection&&indexPuces[selection]) indexPuces[selection].classList.remove("selectionne");
  selection=id;
  if(indexPuces[id]) indexPuces[id].classList.add("selectionne");

  /* Le jeton de pays ne s'affiche que si le champ existe VRAIMENT. Avant,
     son absence retombait sur « France », et la fiche d'une aïeule née à
     Saïgon annonçait qu'elle était restée en France. Un défaut par omission
     affirme quelque chose de faux, ce qui est pire que de ne rien dire. */
  let jet = p.pays==="nf" ? `<span class="jeton j-nf">Nouvelle-France</span>`
          : p.pays==="fr" ? `<span class="jeton j-fr">France</span>` : "";
  if(p.ancetre) jet+=`<span class="jeton j-or">Ancêtre canadien</span>`;
  const brid = BRANCHE_PERS[id]; const brnom = brid && BRANCHE_NOM[brid];
  if(brnom) jet = `<span class="jeton j-br j-${brid}">${brnom}</span>` + jet;
  else if(p.lignee) jet+=`<span class="jeton j-or">Lignée directe</span>`;
  if(p.lacune) jet+=`<span class="jeton j-al">Rattachement non documenté</span>`;
  if((p.sections||[]).some(s=>s.prive)) jet+=`<span class="jeton j-al">Confidentiel</span>`;

  /* l'essentiel, en quelques lignes */
  const L=[];
  const f=(lib,x)=>{ if(x&&x.texte) L.push(`<dt>${lib}</dt><dd>${tl(x.texte)}${cert(x)}</dd>`); };
  f("Naissance", p.naissance);
  if(!p.naissance) f("Baptême", p.bapteme);
  f("Décès", p.deces);
  if(!p.deces) f("Sépulture", p.sepulture);
  if(p.metiers&&p.metiers.length) L.push(`<dt>Métier</dt><dd>${ech2(p.metiers.join(" · "))}</dd>`);
  if(p.lieux&&p.lieux.length){
    const reste=p.lieux.length-1;
    L.push(`<dt>Lieu</dt><dd>${lieuHTML(p.lieux[0])}`
      +(reste?` <span class="f-compte">+${reste}</span>`:"")+`</dd>`);
  }
  (unionsDe[id]||[]).forEach(u=>{
    const a=u.conjoints.find(c=>c!==id);
    const an=((u.mariage&&u.mariage.texte)||"").match(/(1[5-9]\d{2})/);
    L.push(`<dt>Union</dt><dd><span class="lien-pers" data-va="${ech2(a)}">`
      +`${ech2(a?nomComplet(P[a]||{}):"—")}</span>`
      +(an?` <span class="f-compte">${an[1]}</span>`:"")+`</dd>`);
  });
  const par=unionParente[id];
  if(par) L.push(`<dt>Parents</dt><dd>`
    +par.conjoints.map(c=>`<span class="lien-pers" data-va="${ech2(c)}">${ech2(nomComplet(P[c]||{}))}</span>`).join(" &amp; ")
    +`</dd>`);
  const enf=(unionsDe[id]||[]).reduce((a,u)=>a.concat(u.enfants||[]),[]);
  if(enf.length) L.push(`<dt>Enfants</dt><dd>`
    +enf.map(e=>`<span class="lien-pers" data-va="${ech2(e)}">${ech2((P[e]||{}).prenom||e)}</span>`).join(", ")
    +`</dd>`);

  /* Les faits rattachés à plusieurs personnes (C-021) passent avant les
     mentions lues dans les sources, en ordre de date. */
  const evs=(D.evenements||[]).filter(e=>(e.personnes||[]).includes(id))
    .sort((a,b)=>(a.tri||9999)-(b.tri||9999));
  const marq=evs.map(e=>(e.date?`<b>${ech2(e.date)}</b> — `:"")+tl(e.texte)+cert(e))
    .concat((p.marquants||[]).map(m=>tl(m)));
  const pbs=(D.problemes||[]).filter(x=>(x.personnes||[]).includes(id));

  /* ce qui attend derrière « En savoir plus » */
  const sections=p.sections||[];
  const nbEv=sections.reduce((a,s)=>a+(s.type==="chrono"&&Array.isArray(s.contenu)?s.contenu.length:0),0);
  const compte=[];
  if(sections.length) compte.push(sections.length+" section"+(sections.length>1?"s":""));
  if(nbEv) compte.push(nbEv+" événements");
  if(pbs.length) compte.push(pbs.length+" à vérifier");

  const v=vie(p);
  boiteFiche.innerHTML =
    `<div class="f-haut">`
    +(p._photo?`<img class="f-portrait" src="${p._photo}" alt="">`
              :`<div class="f-mono">${ech2(initiales(p))}</div>`)
    +`<div class="f-ident"><h3>${ech2(nomComplet(p))}</h3>`
    +(v?`<div class="f-dates">${ech2(v)}</div>`:"")
    +(p.surnom?`<div class="f-surnom">${ech2(p.surnom)}</div>`:"")
    +`</div><button class="f-fermer" title="Fermer">&times;</button></div>`
    +`<div class="f-corps"><div>${jet}</div>`
    +(L.length?`<dl class="f-faits">${L.join("")}</dl>`:"")
    +(marq.length?`<ul class="f-marquants">${marq.map(m=>`<li>${m}</li>`).join("")}</ul>`:"")
    +pbs.map(x=>`<div class="f-note"><b>${ech2(x.type)} · p. ${ech2(x.pages||"?")}</b>${tl(x.description)}</div>`).join("")
    +`</div>`
    +`<div class="f-bas"><a class="f-plus" href="__DOSSIER_FICHES__/${encodeURIComponent(id)}.html" target="_blank" rel="noopener">En savoir plus</a>`
    +(compte.length?`<span class="f-compte">${compte.join(" · ")}</span>`:"")
    +`</div>`;

  boiteFiche.querySelector(".f-fermer").onclick=e=>{ e.stopPropagation(); fermerFiche(); };
  if(JETON_EDITION){
    const z=boiteFiche.querySelector(".f-portrait, .f-mono");
    z.classList.add("f-modifiable");
    z.title="Cliquer pour choisir une autre photo";
    z.onclick=e=>{ e.stopPropagation(); choisirPortrait(id); };
  }
  boiteFiche.querySelectorAll(".lien-pers").forEach(a=>a.addEventListener("click",e=>{
    e.stopPropagation();
    const w=a.getAttribute("data-va");
    if(!P[w]) return;
    if(indexPuces[w]){ centrer(w); setTimeout(()=>ouvrirFiche(w),170); } else ouvrirFiche(w);
  }));
  positionnerFiche(id);
  boiteFiche.classList.add("ouverte");
}

function abreger(t,n){ t=String(t||""); return t.length>n ? t.slice(0,n-1)+"…" : t; }

/* ---- lieux cliquables vers une carte ----
   La requête ne part jamais du texte brut : il contient des dates entre
   parenthèses, et « Champlain » tout seul tombe en France. On passe par la
   table meta.carte.lieux, corrigeable à la main ; une entrée vide = pas de lien. */
const CARTE = (D.meta && D.meta.carte) || {};
function nettoyerLieu(t){
  return String(t||"").replace(/\([^)]*\)/g," ").replace(/\s{2,}/g," ").trim().replace(/^[,;\s]+|[,;\s]+$/g,"");
}
function urlCarte(texte){
  if(CARTE.actif===false) return null;
  const table=CARTE.lieux||{};
  let q = Object.prototype.hasOwnProperty.call(table,texte) ? table[texte] : nettoyerLieu(texte);
  if(!q) return null;
  return (CARTE.service||"https://www.google.com/maps/search/?api=1&query=") + encodeURIComponent(q);
}
function lieuHTML(texte){
  const u=urlCarte(texte);
  return u ? `<a class="lieu" href="${u}" target="_blank" rel="noopener" title="Voir sur la carte">${ech2(texte)}</a>`
           : ech2(texte);
}

/* Reconnaissance des toponymes DANS les textes libres.
   On travaille sur du texte déjà échappé ; une seule occurrence par bloc. */
const TOPO=(CARTE.toponymes)||{};
const TOPO_NOMS=Object.keys(TOPO).filter(k=>TOPO[k]).sort((a,b)=>b.length-a.length);
function aplatir(s){ return s.replace(/’/g,"'").toLowerCase(); }
function estLettre(c){ return !!c && /[0-9A-Za-zÀ-ÖØ-öø-ÿ'’]/.test(c); }
function lierLieux(txt){
  if(CARTE.actif===false || !TOPO_NOMS.length || !txt) return txt;
  let res=String(txt), pris=[];
  for(const nom of TOPO_NOMS){
    const cible=aplatir(nom), n=cible.length;
    let i=-1, depart=0;
    for(;;){
      i=aplatir(res).indexOf(cible, depart);
      if(i<0) break;
      const dansBalise = res.lastIndexOf("<",i) > res.lastIndexOf(">",i);
      const chevauche = pris.some(p=> i<p[1] && i+n>p[0]);
      if(!estLettre(res[i-1]) && !estLettre(res[i+n]) && !dansBalise && !chevauche) break;
      depart=i+1;
    }
    if(i<0) continue;
    const brut=res.slice(i,i+n);
    const a=`<a class="lieu" href="${(CARTE.service||"")+encodeURIComponent(TOPO[nom])}"`
          +` target="_blank" rel="noopener" title="Voir sur la carte">${brut}</a>`;
    res=res.slice(0,i)+a+res.slice(i+n);
    const d=a.length-n;
    pris=pris.map(p=> p[0]>i ? [p[0]+d,p[1]+d] : p);
    pris.push([i,i+a.length]);
  }
  return res;
}
/* texte échappé puis enrichi de ses liens de lieux */
function tl(s){ return lierLieux(ech2(s)); }

/* la carte se colle au médaillon, et bascule de côté si elle déborde */
function positionnerFiche(id){
  const g=indexPuces[id];
  const l=boiteFiche.offsetWidth, h=boiteFiche.offsetHeight;
  const vw=window.innerWidth, vh=window.innerHeight, M=12, HAUT=70;
  let x,y;
  if(g){
    const b=g.getBoundingClientRect();
    x=b.right+14;
    if(x+l>vw-M) x=b.left-l-14;
    if(x<M) x=Math.min(Math.max(b.left,M), vw-l-M);
    y=b.top+b.height/2-h/2;
  }else{ x=vw-l-M; y=HAUT+18; }
  boiteFiche.style.left=Math.round(Math.max(M,Math.min(x,vw-l-M)))+"px";
  boiteFiche.style.top =Math.round(Math.max(HAUT,Math.min(y,vh-h-M)))+"px";
}

function fermerFiche(){
  boiteFiche.classList.remove("ouverte");
  if(selection&&indexPuces[selection]) indexPuces[selection].classList.remove("selectionne");
  selection=null;
}

function centrer(id){
  const g=indexPuces[id]; if(!g) return;
  const m=/translate\(([-\d.]+),([-\d.]+)\)/.exec(g.getAttribute("transform")); if(!m) return;
  const r=toile.getBoundingClientRect();
  const lx=mode==="portraits"?MED_L/2:FIC_L/2, ly=mode==="portraits"?MED_H/2:FIC_H/2;
  tx=r.width*0.36-(+m[1]+lx)*ech; ty=r.height/2-(+m[2]+ly)*ech; appliquer();
}

/* ======================= recherche & filtres ======================= */
const rech=document.getElementById("rech"), boite=document.getElementById("boite-rech"),
      compteur=document.getElementById("compteur"), bLig=document.getElementById("b-lignee");
function norm(s){ return (s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,""); }
function chercher(){
  const q=norm(rech.value.trim());
  boite.classList.toggle("pleine",!!q);
  if(!q){ Object.values(indexPuces).forEach(g=>g.classList.remove("eteint","trouve"));
    compteur.textContent=""; appliquerLignee(); return; }
  /* La recherche doit porter sur TOUT l'arbre, pas sur ce qui est
     actuellement dessiné : chercher dans un arbre replié ne trouverait
     presque rien, et l'utilisateur en concluerait que la personne n'y est
     pas. On cherche donc dans les données, on ouvre les chemins, et on
     redessine une fois. */
  const assortis = Object.keys(P).filter(id=>{
    const p=P[id];
    return norm([nomComplet(p),p.surnom,(p.variantes||[]).join(" "),
      (p.metiers||[]).join(" "),(p.lieux||[]).join(" ")].join(" ")).includes(q);
  });
  /* Ouvrir d'abord les chemins, redessiner, PUIS surligner. L'ordre
     compte : surligner avant le redessin peignait un DOM qui allait être
     jeté, et le compteur restait vide alors que la recherche avait bien
     trouvé. Le défaut ne se voyait qu'en cherchant pour de vrai. */
  let ouvert=false;
  assortis.forEach(id=>{ if(indexNoeuds[id] && !indexPuces[id]){
    if(ouvrirChemin(id)) ouvert=true; } });
  if(ouvert) redessine(true);
  let n=0;
  Object.entries(indexPuces).forEach(([id,g])=>{
    const ok=assortis.indexOf(id)>=0;
    g.classList.toggle("trouve",ok); g.classList.toggle("eteint",!ok);
    if(ok) n++;
  });
  const caches = assortis.length - n;
  compteur.textContent = n+(n>1?" trouvés":" trouvé")
    + (caches>0 ? " · "+caches+" replié"+(caches>1?"s":"") : "");
}
function appliquerLignee(){
  if(bLig.getAttribute("aria-pressed")!=="true") return;
  Object.entries(indexPuces).forEach(([id,g])=>{ if(!(P[id]||{}).lignee) g.classList.add("eteint"); });
}
rech.addEventListener("input",chercher);
document.getElementById("effacer").onclick=()=>{rech.value="";chercher();rech.focus();};
bLig.onclick=()=>{
  const on=bLig.getAttribute("aria-pressed")!=="true";
  bLig.setAttribute("aria-pressed",on);
  Object.values(indexPuces).forEach(g=>g.classList.remove("eteint"));
  chercher(); appliquerLignee();
};

/* ======================= bascule de mode ======================= */
const bP=document.getElementById("m-portraits"), bF=document.getElementById("m-fiches");
function setMode(m){
  if(m===mode) return;
  mode=m;
  bP.setAttribute("aria-pressed", m==="portraits");
  bF.setAttribute("aria-pressed", m==="fiches");
  rendre(false);
}
bP.onclick=()=>setMode("portraits");
bF.onclick=()=>setMode("fiches");

/* ======================= problèmes ======================= */
const vPb=document.getElementById("problemes"), bPb=document.getElementById("b-pb");
document.getElementById("n-pb").textContent=(D.problemes||[]).length?"("+D.problemes.length+")":"";
document.getElementById("liste-pb").innerHTML=(D.problemes||[]).map(x=>{
  const qui=(x.personnes||[]).map(i=>nomComplet(P[i]||{})).filter(s=>s.trim()).join(", ");
  return `<div class="pb"><div class="pb-tete">
    <span class="pb-type g-${ech2(x.gravite||"faible")}">${ech2(x.type)}</span>
    <span class="pb-pages">p. ${ech2(x.pages||"?")}</span>
    ${qui?`<span class="pb-pages">· ${ech2(qui)}</span>`:""}
  </div><p>${ech2(x.description)}</p></div>`;
}).join("");
bPb.onclick=()=>{ const on=!vPb.classList.contains("ouvert");
  vPb.classList.toggle("ouvert",on); bPb.setAttribute("aria-pressed",on); };

/* ======================= thème ======================= */
document.getElementById("b-theme").onclick=()=>{
  const sombre=getComputedStyle(document.body).backgroundColor.match(/\d+/g).map(Number)[0]<100;
  document.documentElement.setAttribute("data-theme", sombre?"light":"dark");
};

/* ======================= clavier ======================= */
document.addEventListener("keydown",e=>{
  if(e.key==="Escape"){ fermerFiche(); vPb.classList.remove("ouvert"); bPb.setAttribute("aria-pressed",false);
    if(rech.value){ rech.value=""; chercher(); } }
  if(e.key==="/"&&document.activeElement!==rech){ e.preventDefault(); rech.focus(); }
});

/* ======================= modification directe ======================= */
/* Servi par Serveur_Local.bat, l'arbre se modifie : un clic sur le visage
   dans la carte, on choisit une image, le serveur la range, refait l'arbre,
   et la page revient au même endroit, la même carte ouverte. Ouvert par
   double-clic, rien de tout cela n'existe : il ne demande rien à personne. */
const SOURCE_DONNEES="__SOURCE__";
let JETON_EDITION=null;
const fPortraitArbre=document.createElement("input");
fPortraitArbre.type="file"; fPortraitArbre.accept="image/*"; fPortraitArbre.hidden=true;
document.body.appendChild(fPortraitArbre);
let portraitPour=null;
function choisirPortrait(id){ portraitPour=id; fPortraitArbre.value=""; fPortraitArbre.click(); }
function garderVue(){
  try{ sessionStorage.setItem("vue-arbre", JSON.stringify({sel:selection, tx, ty, ech, mode})); }catch(e){}
}
function avis(txt, erreur){
  let t=document.getElementById("avis-arbre");
  if(!t){ t=document.createElement("div"); t.id="avis-arbre"; document.body.appendChild(t); }
  t.textContent=txt; t.className="visible"+(erreur?" erreur":"");
  clearTimeout(t._m); t._m=setTimeout(()=>t.className="", erreur?8000:2600);
}
fPortraitArbre.addEventListener("change",()=>{
  const f=fPortraitArbre.files[0], id=portraitPour; if(!f||!id) return;
  const l=new FileReader();
  l.onload=()=>{
    avis("Enregistrement du portrait…");
    fetch("/_modifier",{method:"POST",headers:{"Content-Type":"application/json","X-Jeton":JETON_EDITION},
      body:JSON.stringify({op:"portrait",source:SOURCE_DONNEES,pid:id,donnee:l.result})})
     .then(r=>r.json()).then(o=>{
       if(o&&o.ok){ garderVue(); try{ sessionStorage.setItem("avis-arbre", o.message); }catch(e){} location.reload(); }
       else avis("Non enregistré : "+((o&&o.erreur)||"raison inconnue"), true);
     }).catch(()=>avis("Le serveur ne répond plus : rien n'a été enregistré.", true));
  };
  l.readAsDataURL(f);
});
if(location.protocol==="http:"||location.protocol==="https:"){
  fetch("/_jeton").then(r=>r.ok?r.json():null).then(o=>{
    if(!o||!o.jeton) return;
    JETON_EDITION=o.jeton;
    document.body.classList.add("edition");
    if(selection) ouvrirFiche(selection);
    /* Une fiche modifiée dans un autre onglet : l'arbre se refait aussi. */
    try{ new BroadcastChannel("arbre-maj").onmessage=m=>{
      if(m.data&&m.data.source===SOURCE_DONNEES){ garderVue(); location.reload(); } }; }catch(e){}
  }).catch(()=>{});
}

rendre(false);
/* Retour après une modification : même vue, même carte ouverte. */
(function reprendre(){
  let v=null;
  try{ v=JSON.parse(sessionStorage.getItem("vue-arbre")||"null"); sessionStorage.removeItem("vue-arbre"); }catch(e){}
  if(!v) return;
  if(v.mode&&v.mode!==mode) setMode(v.mode);
  if(v.sel&&indexNoeuds[v.sel]&&!indexPuces[v.sel]){ ouvrirChemin(v.sel); rendre(true); }
  if([v.tx,v.ty,v.ech].every(Number.isFinite)){ tx=v.tx; ty=v.ty; ech=v.ech; appliquer(); }
  if(v.sel&&P[v.sel]) ouvrirFiche(v.sel);
  try{ const m=sessionStorage.getItem("avis-arbre"); if(m){ sessionStorage.removeItem("avis-arbre");
    avis(m.charAt(0).toUpperCase()+m.slice(1)+"."); } }catch(e){}
})();
</script>
</body>
</html>
"""


def charger_photo(chemin: Path):
    """Lit une image, la réduit si possible, renvoie une URI data:."""
    donnees = chemin.read_bytes()
    try:
        from PIL import Image, ImageOps
        im = Image.open(io.BytesIO(donnees))
        im.draft("RGB", (COTE_MAX * 2, COTE_MAX * 2))   # décodage JPEG réduit : bien plus rapide
        im = ImageOps.exif_transpose(im)     # une photo de téléphone couchée se redresse
        im = im.convert("RGB")
        # recadrage carré centré, puis réduction
        c = min(im.size)
        g = (im.width - c) // 2
        h = (im.height - c) // 2
        im = im.crop((g, h, g + c, h + c))
        if c > COTE_MAX:
            im = im.resize((COTE_MAX, COTE_MAX), Image.LANCZOS)
        tampon = io.BytesIO()
        im.save(tampon, format="JPEG", quality=QUALITE, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(tampon.getvalue()).decode(), len(tampon.getvalue())
    except Exception:
        mt = mimetypes.guess_type(chemin.name)[0] or "image/jpeg"
        return "data:" + mt + ";base64," + base64.b64encode(donnees).decode(), len(donnees)


def charger_image(chemin: Path, cote=COTE_GALERIE):
    """Une photo de galerie : entière (pas de recadrage), réduite à « cote »
    pixels au plus grand côté."""
    donnees = chemin.read_bytes()
    try:
        from PIL import Image, ImageOps
        im = Image.open(io.BytesIO(donnees))
        im.draft("RGB", (cote, cote))
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((cote, cote), Image.LANCZOS)
        tampon = io.BytesIO()
        im.save(tampon, format="JPEG", quality=84, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(tampon.getvalue()).decode()
    except Exception:
        mt = mimetypes.guess_type(chemin.name)[0] or "image/jpeg"
        return "data:" + mt + ";base64," + base64.b64encode(donnees).decode()


def photos_galerie(dossier: Path, pid: str):
    """Les photos de galerie : « <id>-<n>.<ext> », en ordre numérique. Le
    nom nu est réservé au portrait (C-017)."""
    motif = re.compile(re.escape(pid) + r"-(\d+)(\.[A-Za-z]+)$")
    trouvees = []
    for f in dossier.iterdir():
        m = motif.match(f.name)
        if m and f.is_file() and f.suffix.lower() in EXTENSIONS:
            trouvees.append((int(m.group(1)), f))
    return [f for _, f in sorted(trouvees)]


def trouver_photo(dossier: Path, pid: str, nom_declare=None):
    if nom_declare:
        p = dossier / nom_declare
        if p.exists():
            return p
        p = dossier.parent / nom_declare
        if p.exists():
            return p
        return None
    for ext in EXTENSIONS:
        p = dossier / (pid + ext)
        if p.exists():
            return p
    return None


GABARIT_PAGE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__NOM__ — __TITRE_ARBRE__</title>
<style>
:root{
  --bg:#f8f5ec; --surface:#fffdf7; --surface-2:#f0e9d9;
  --ink:#241f17; --muted:#6b6150; --faint:#9b9079;
  --line:#cfc3a9; --line-soft:#e4dbc7;
  --jean:#2f5d8f; --trinh:#2f7d4f; --gagne:#7c5a86;
  --or:#b4862c; --or-bg:#f8edd4;
  --fr:#b08a3e; --fr-bg:#f6ecd6;
  --nf:#2f7d4f; --nf-bg:#dff0e4;
  --alerte:#a8452a; --alerte-bg:#f9e4dd;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#15130e; --surface:#201d16; --surface-2:#2b2719;
  --ink:#f3eee3; --muted:#a89c85; --faint:#79705d;
  --line:#474032; --line-soft:#332e24;
  --or:#dcae58; --or-bg:#34280f;
  --fr:#d2a85e; --fr-bg:#2e2412;
  --nf:#62c48f; --nf-bg:#152c1f;
  --alerte:#e08a6c; --alerte-bg:#36201a;
}}
*{box-sizing:border-box}
body{margin:0; background:var(--bg); color:var(--ink);
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  -webkit-font-smoothing:antialiased; line-height:1.55}
a{color:var(--or)}
.lieu{color:var(--or); text-decoration:underline dotted;
  text-decoration-color:color-mix(in srgb, var(--or) 50%, transparent);
  text-underline-offset:2.5px}
.lieu::after{content:""; display:inline-block; width:.66em; height:.66em; margin-left:.2em;
  vertical-align:-.02em; background-color:currentColor; opacity:.75;
  -webkit-mask:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%3E%3Cpath%20d%3D%22M12%202a7%207%200%200%200-7%207c0%205.3%207%2013%207%2013s7-7.7%207-13a7%207%200%200%200-7-7zm0%209.6A2.6%202.6%200%201%201%2012%206.4a2.6%202.6%200%200%201%200%205.2z%22%2F%3E%3C%2Fsvg%3E") center/contain no-repeat; mask:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%3E%3Cpath%20d%3D%22M12%202a7%207%200%200%200-7%207c0%205.3%207%2013%207%2013s7-7.7%207-13a7%207%200%200%200-7-7zm0%209.6A2.6%202.6%200%201%201%2012%206.4a2.6%202.6%200%200%201%200%205.2z%22%2F%3E%3C%2Fsvg%3E") center/contain no-repeat}
.lieu:hover{text-decoration-style:solid; text-decoration-color:var(--or)}
.lieu:hover::after{opacity:1}
.bandeau{position:sticky; top:0; z-index:5; background:color-mix(in srgb,var(--surface) 94%, transparent);
  backdrop-filter:blur(10px); border-bottom:1px solid var(--line-soft);
  padding:11px 24px; display:flex; align-items:center; gap:14px; font-size:13px}
.bandeau .retour{text-decoration:none; font-weight:600}
.bandeau .retour:hover{text-decoration:underline; text-underline-offset:2px}
.bandeau .fil{color:var(--faint)}
main{max-width:1180px; margin:0 auto; padding:30px 24px 90px;
  display:grid; grid-template-columns:1fr; gap:0 44px}
@media(min-width:1040px){ main{grid-template-columns:186px minmax(0,1fr)} }
.cote{display:none}
@media(min-width:1040px){ .cote{display:block; position:sticky; top:72px; align-self:start; padding-top:8px} }
.cote a{display:block; font-size:12.2px; color:var(--muted); text-decoration:none;
  padding:5px 0 5px 11px; border-left:2px solid var(--line-soft); line-height:1.35}
.cote a:hover{color:var(--or); border-left-color:var(--or)}
.colonne{min-width:0}
.entete{display:flex; gap:22px; align-items:center; margin:0 0 28px; flex-wrap:wrap}
.portrait{width:112px; height:112px; border-radius:50%; object-fit:cover;
  border:4px solid var(--or); background:var(--surface-2); flex-shrink:0}
.mono{width:112px; height:112px; border-radius:50%; background:var(--surface-2);
  border:4px solid var(--line); display:grid; place-items:center;
  font-size:36px; font-weight:600; color:var(--faint); flex-shrink:0}
h1{margin:0 0 3px; font-size:31px; font-weight:600; line-height:1.14; letter-spacing:-.2px}
.dates{margin:0; font-size:15px; color:var(--muted); font-variant-numeric:tabular-nums}
.surnom{margin:2px 0 0; font-size:14px; color:var(--faint); font-style:italic}
.jetons{margin-top:9px}
.jeton{display:inline-block; font-size:10.5px; padding:2.5px 9px; border-radius:99px;
  margin:0 5px 5px 0; font-weight:600; letter-spacing:.2px}
.j-fr{background:var(--fr-bg); color:var(--fr)}
.j-nf{background:var(--nf-bg); color:var(--nf)}
.j-or{background:var(--or-bg); color:var(--or)}
.j-al{background:var(--alerte-bg); color:var(--alerte)}
section{margin:0 0 30px; scroll-margin-top:72px}
h2{margin:0 0 13px; font-size:11px; text-transform:uppercase; letter-spacing:1.1px;
  color:var(--faint); font-weight:700; padding-bottom:7px; border-bottom:1px solid var(--line-soft)}
dl.faits{display:grid; grid-template-columns:auto 1fr; gap:9px 18px; margin:0; font-size:14.6px}
dl.faits dt{color:var(--faint); font-size:10.5px; text-transform:uppercase; letter-spacing:.7px;
  font-weight:700; padding-top:3px; white-space:nowrap}
dl.faits dd{margin:0}
dl.faits dd small{display:block; color:var(--muted); font-size:12.6px; line-height:1.45; margin-top:2px}
ul.marquants{list-style:none; margin:0; padding:0}
ul.marquants li{position:relative; padding-left:19px; font-size:15px; line-height:1.55; margin-bottom:11px}
ul.marquants li::before{content:""; position:absolute; left:0; top:9px; width:7px; height:7px;
  border-radius:50%; background:var(--or)}
.texte p{font-size:15.2px; line-height:1.68; margin:0 0 13px; max-width:68ch}
ul.puces{margin:0; padding-left:19px; font-size:14.8px}
ul.puces li{margin-bottom:8px; line-height:1.55}
.intro{font-size:13.4px; color:var(--muted); font-style:italic; margin:0 0 13px; line-height:1.5}
.chrono{list-style:none; margin:0; padding:0 0 0 3px; position:relative}
.chrono::before{content:""; position:absolute; left:5.5px; top:8px; bottom:8px; width:1.5px; background:var(--line-soft)}
.chrono li{position:relative; padding:0 0 18px 26px; font-size:14.6px; line-height:1.55}
.chrono li::before{content:""; position:absolute; left:0; top:7px; width:10px; height:10px;
  border-radius:50%; background:var(--bg); border:2.5px solid var(--or)}
.chrono .d{display:block; font-size:11.4px; color:var(--faint); font-variant-numeric:tabular-nums;
  letter-spacing:.3px; margin-bottom:1px}
.chrono .t{font-weight:600}
.chrono .x{display:block; color:var(--muted); font-size:13.6px; line-height:1.52; margin-top:3px; max-width:62ch}
table{width:100%; border-collapse:collapse; font-size:14px; margin:0}
th{text-align:left; font-size:10.5px; text-transform:uppercase; letter-spacing:.7px; color:var(--faint);
  border-bottom:1.5px solid var(--line); padding:7px 12px 7px 0; font-weight:700}
td{padding:9px 12px 9px 0; border-bottom:1px solid var(--line-soft); vertical-align:top; line-height:1.48}
.voile{border:1px dashed var(--alerte); border-radius:9px; background:var(--alerte-bg); padding:15px 17px}
.voile button{border:0; background:transparent; cursor:pointer; color:var(--alerte); font:inherit;
  font-size:14px; font-weight:600; padding:0; text-align:left; line-height:1.5}
.voile button span{display:block; font-weight:400; color:var(--muted); font-size:12.6px; margin-top:3px}
.voile[data-ouvert="1"]{background:transparent; border-style:solid; border-color:var(--line-soft)}
.avis{background:var(--alerte-bg); border-left:3px solid var(--alerte); padding:13px 15px;
  border-radius:0 7px 7px 0; font-size:14px; line-height:1.55; margin:0 0 11px}
.avis b{color:var(--alerte); text-transform:uppercase; font-size:10.5px; letter-spacing:.7px}
.src{font-size:13px; color:var(--faint); font-style:italic; line-height:1.55; margin:0}

/* ---- ajouts : portrait, dates, photos, recettes ---- */
.zone-portrait{position:relative; cursor:pointer; border-radius:50%}
.zone-portrait::after{content:"Ajouter une photo"; position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center; text-align:center;
  border-radius:50%; background:color-mix(in srgb,var(--ink) 62%,transparent);
  color:#fff; font-size:12px; font-weight:600; opacity:0; transition:opacity .14s;
  padding:0 14px; line-height:1.3}
.zone-portrait:hover::after, .zone-portrait:focus-visible::after{opacity:1}
.b-modif{border:1px solid var(--line); background:var(--surface); color:var(--muted);
  font:inherit; font-size:11px; border-radius:6px; padding:1px 7px; margin-left:8px;
  cursor:pointer; vertical-align:2px}
.b-modif:hover{border-color:var(--or); color:var(--or)}
.b-ajout{border:1px dashed var(--line); background:transparent; color:var(--muted);
  font:inherit; font-size:13.5px; border-radius:8px; padding:9px 15px; cursor:pointer}
.b-ajout:hover{border-color:var(--or); color:var(--or); border-style:solid}
.saisie{font:inherit; font-size:14.6px; padding:5px 9px; border:1px solid var(--or);
  border-radius:6px; background:var(--surface); color:var(--ink); min-width:230px}
.saisie-l{width:100%; box-sizing:border-box; margin-bottom:8px}
textarea.saisie{min-height:110px; line-height:1.55; resize:vertical}
.vignettes{display:flex; flex-wrap:wrap; gap:13px; margin:0 0 13px}
.vignette{width:132px}
.vignette img{width:132px; height:132px; object-fit:cover; border-radius:8px;
  border:1px solid var(--line)}
.recette{border-left:3px solid var(--or); padding:2px 0 2px 14px; margin:0 0 15px}
.recette h3{margin:0 0 5px; font-size:15.5px}
.recette p{margin:0; white-space:pre-wrap; line-height:1.6}
.barre-ajouts{position:fixed; left:50%; transform:translateX(-50%); bottom:20px;
  background:var(--surface); border:1px solid var(--or); border-radius:11px;
  padding:11px 17px; display:none; align-items:center; gap:15px; z-index:40;
  box-shadow:0 6px 26px color-mix(in srgb,var(--ink) 17%,transparent); font-size:14px}
.barre-ajouts.visible{display:flex}
.barre-ajouts button{border:0; background:var(--or); color:#fff; font:inherit;
  font-weight:600; border-radius:7px; padding:7px 15px; cursor:pointer}
.barre-ajouts .quoi{color:var(--muted)}
.note-ajout{font-size:12.4px; color:var(--faint); line-height:1.55; margin:9px 0 0;
  font-style:italic}
/* ---- modification sur place (C-021) ---- */
[hidden]{display:none !important}
.vide-edition, .b-plus-ed, .crayon{display:none}
body.edition .vide-edition{display:revert}
body.edition .b-plus-ed{display:inline-block}
body.edition .ed, body.ajouts [data-ed="fait"]{cursor:pointer; position:relative; border-radius:6px;
  transition:background-color .12s}
body.edition .ed:hover, body.ajouts [data-ed="fait"]:hover{
  background:color-mix(in srgb, var(--or) 9%, transparent);
  box-shadow:0 0 0 5px color-mix(in srgb, var(--or) 9%, transparent)}
body.edition .crayon, body.ajouts [data-ed="fait"] .crayon{display:inline-block; border:0;
  background:transparent; color:var(--faint); font:inherit; font-size:13px; cursor:pointer;
  margin-left:7px; padding:0 3px; opacity:.45; vertical-align:1px}
body.edition .ed:hover > .crayon, body.ajouts [data-ed="fait"]:hover > .crayon,
.crayon:focus-visible{opacity:1; color:var(--or)}
@media (hover:none){ body.edition .crayon{opacity:.8} }
.en-edition{background:transparent !important; box-shadow:none !important; cursor:default !important}
.en-edition > :not(.editeur){display:none !important}
.v.vide{color:var(--faint); font-style:italic}
.en-attente{font-size:10px; font-weight:700; color:var(--or); background:var(--or-bg);
  padding:1.5px 6px; border-radius:4px; margin-left:7px; font-style:normal}
.liste-ed{list-style:none; margin:0; padding:0}
.liste-ed li{margin:0 0 3px}
.liste-ed.puces{list-style:disc; padding-left:19px; font-size:14.8px}
.liste-ed.puces li{margin-bottom:8px; line-height:1.55}
.b-plus-ed{border:0; background:transparent; color:var(--or); font:inherit; font-size:12.6px;
  padding:3px 0; cursor:pointer; font-weight:600}
.b-plus-ed:hover{text-decoration:underline; text-underline-offset:2px}
.editeur{display:block; margin:6px 0 10px; padding:13px 14px; border:1px solid var(--or);
  border-radius:9px; background:var(--surface); box-shadow:0 4px 18px color-mix(in srgb,var(--ink) 10%,transparent);
  max-width:620px; cursor:default; font-size:14px; text-transform:none; letter-spacing:0; font-weight:400}
.ed-champ{display:block; margin:0 0 9px}
.ed-champ > span{display:block; font-size:10.5px; text-transform:uppercase; letter-spacing:.7px;
  color:var(--faint); font-weight:700; margin:0 0 4px}
.editeur .saisie{min-width:0; width:100%; margin:0}
.editeur select.saisie{width:auto}
.ed-note{font-size:12.6px; color:var(--muted); margin:0 0 10px; line-height:1.5}
.ed-boutons{display:flex; gap:8px; flex-wrap:wrap; align-items:center}
.ed-ok, .ed-non, .ed-retirer, .b-petit{font:inherit; font-size:13px; border-radius:7px;
  padding:6px 13px; cursor:pointer}
.ed-ok{border:0; background:var(--or); color:#fff; font-weight:600}
.ed-non{border:1px solid var(--line); background:transparent; color:var(--muted)}
.ed-retirer{border:1px solid var(--alerte); background:transparent; color:var(--alerte); margin-left:auto}
.ed-retirer:hover{background:var(--alerte-bg)}
.b-petit{border:1px solid var(--line); background:transparent; color:var(--muted); font-size:12px;
  padding:3px 10px; margin-top:6px}
.b-petit:hover{border-color:var(--alerte); color:var(--alerte)}
.choix-pers .cp-puces{display:flex; flex-wrap:wrap; gap:6px; margin:0 0 7px}
.cp-puce{background:var(--or-bg); color:var(--ink); border-radius:99px; padding:2px 4px 2px 11px; font-size:13px}
.cp-puce button{border:0; background:transparent; color:var(--muted); cursor:pointer; font:inherit; padding:0 5px}
.cp-puce button:hover{color:var(--alerte)}
ul.marquants li.ev small, ul.marquants li small{display:block; color:var(--muted); font-size:12.8px; margin-top:2px}
.ev-date{display:block; font-size:11.4px; color:var(--faint); font-variant-numeric:tabular-nums; letter-spacing:.3px}
.ev-src{font-style:italic}
figure.vignette{margin:0}
figure.vignette img{display:block}
figure.vignette figcaption{font-size:12.4px; color:var(--muted); line-height:1.4; margin-top:5px}
.toast{position:fixed; left:50%; bottom:22px; transform:translate(-50%, 16px); opacity:0;
  pointer-events:none; transition:opacity .18s, transform .18s; z-index:60; max-width:min(560px, calc(100vw - 32px));
  background:var(--ink); color:var(--bg); padding:10px 16px; border-radius:9px; font-size:14px; line-height:1.45;
  box-shadow:0 6px 26px color-mix(in srgb,var(--ink) 25%,transparent)}
.toast.visible{opacity:1; transform:translate(-50%, 0)}
.toast.erreur{background:var(--alerte); color:#fff}
body.edition .note-fichier{display:none}
.rel{display:grid; grid-template-columns:auto 1fr; gap:9px 18px; font-size:14.6px; margin:0}
.rel dt{color:var(--faint); font-size:10.5px; text-transform:uppercase; letter-spacing:.7px;
  font-weight:700; padding-top:3px; white-space:nowrap}
.rel dd{margin:0}
.marque-cert{font-size:10px; font-weight:700; padding:1.5px 6px; border-radius:4px; margin-left:6px; letter-spacing:.2px}
.c-approximative{background:var(--surface-2); color:var(--muted)}
.c-deduite{background:var(--fr-bg); color:var(--fr)}
.c-divergente,.c-incoherente,.c-inconnue{background:var(--alerte-bg); color:var(--alerte)}
footer{border-top:1px solid var(--line-soft); margin:46px 0 0; padding:18px 0 0;
  font-size:12px; color:var(--faint); line-height:1.6}
</style>
</head>
<body>
<div class="bandeau"><a class="retour" href="../__ARBRE__">&larr; L'arbre</a><span class="fil">__TITRE_ARBRE__</span>__BOUTON_ADMIN__</div>
<main>
  <nav class="cote">__COTE__</nav>
  <div class="colonne">
    <div class="entete">__PORTRAIT__
      <div><h1>__NOM__</h1>__DATES____SURNOM__<div class="jetons">__JETONS__</div></div>
    </div>
    __CORPS__
    <footer>__PIED__</footer>
  </div>
</main>
<div class="barre-ajouts" id="barre"><span class="quoi" id="quoi"></span>
  <button type="button" id="b-enregistrer">Enregistrer mes ajouts</button></div>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
__DIALOGUE_ADMIN__
<input type="file" id="f-portrait" accept="image/*" hidden>
<input type="file" id="f-photos" accept="image/*" multiple hidden>
<script>
"use strict";
/* ===================================================================
   MODIFIER UNE FICHE — C-021.

   DEUX CHEMINS, UNE SEULE PAGE. C'est la page qui constate comment elle a
   été ouverte, et non deux versions à maintenir : deux versions
   divergeraient, et c'est celle qu'on teste le moins qui partirait chez la
   parenté.

   Servie par Serveur_Local.bat : on clique sur une valeur, on corrige, on
   enregistre — le serveur écrit les données, refait l'arbre, et la page se
   recharge d'elle-même. Rien n'attend, il n'y a pas de bouton « Enregistrer
   mes ajouts ».

   Ouverte par double-clic (« file:// ») : une page ne peut pas écrire sur
   le disque. Elle garde alors le chemin d'origine : portrait, dates,
   photos et recettes s'accumulent, et « Enregistrer mes ajouts » rend un
   fichier à déposer sur Appliquer_Ajouts.bat. C'est le chemin de la
   parenté ; le contrôle T-40 le garde.
   =================================================================== */
const PID = "__PID__", PNOM = "__NOMJS__", SOURCE = "__SOURCE__";
const PERSONNES = __PERSONNES__;            /* [id, nom, années] */
const NOMS = {}; PERSONNES.forEach(x=>{ NOMS[x[0]] = x; });
const SERVIE = location.protocol === "http:" || location.protocol === "https:";
const CERTS = [["", "selon la saisie"], ["attestee", "attestée"],
  ["approximative", "approximative"], ["deduite", "déduite"],
  ["divergente", "divergente"], ["incoherente", "incohérente"], ["inconnue", "inconnue"]];
let JETON = null;
/* Ce qu'une couche optionnelle peut ajouter aux envois (en-têtes) et à
   l'affichage. Vide par défaut. */
const EXTRA = {entetes:()=>({}), apresChargement:()=>{}, indice:()=>"",
  noteAttestee:"Fait attesté par la source : une saisie à la main ne le remplace pas."};

/* ---------- petits outils ---------- */
const $ = (s,r)=>(r||document).querySelector(s);
const $$ = (s,r)=>[...(r||document).querySelectorAll(s)];
function mk(t, props, ...enf){
  const e = document.createElement(t);
  Object.assign(e, props||{});
  enf.forEach(c=>{ if(c!=null) e.append(c); });
  return e;
}
function val(el){ try { return JSON.parse(el.dataset.val || "null"); } catch(e){ return null; } }
function lire(fichier, suite){
  const l = new FileReader();
  l.onload = () => suite(l.result);
  l.readAsDataURL(fichier);
}
let minuterie = null;
function dire(txt, genre){
  const t = $("#toast");
  t.textContent = txt;
  t.className = "toast visible " + (genre||"");
  clearTimeout(minuterie);
  if(genre !== "attente")
    minuterie = setTimeout(()=>t.classList.remove("visible"), genre==="erreur" ? 9000 : 2800);
}

/* ===================================================================
   L'ÉDITEUR EN PLACE — un seul, pour tout ce qui se modifie.
   Il s'ouvre DANS l'élément cliqué ; le contenu d'origine est masqué, pas
   détruit, donc « Annuler » rend exactement ce qui était là (défaut D-1 :
   l'ancienne boîte remplaçait l'affichage par « — »).
   =================================================================== */
let ouvert = null;
function fermerEditeur(){ if(ouvert){ const o = ouvert; ouvert = null; o(); } }

function choixPersonnes(ids){
  const w = mk("div", {className:"choix-pers"});
  const puces = mk("div", {className:"cp-puces"});
  let choisis = [...ids];
  const dl = mk("datalist", {id:"dl-" + Math.random().toString(36).slice(2)});
  PERSONNES.forEach(([id, nom, v])=>dl.append(mk("option", {value: nom + (v ? " (" + v + ")" : "") + " · " + id})));
  const i = mk("input", {className:"saisie", type:"text",
    placeholder:"Ajouter une personne : tapez un nom puis choisissez"});
  i.setAttribute("list", dl.id);
  function rendre(){
    puces.textContent = "";
    choisis.forEach(id=>{
      const b = mk("span", {className:"cp-puce"}, (NOMS[id] ? NOMS[id][1] : id) + " ");
      const x = mk("button", {type:"button", textContent:"×", title:"Retirer de ce fait"});
      x.onclick = ()=>{ choisis = choisis.filter(y=>y!==id); rendre(); };
      b.append(x); puces.append(b);
    });
  }
  const prendre = ()=>{
    const m = /· ([^·]+)$/.exec(i.value);
    const id = m && m[1].trim();
    if(id && NOMS[id] && !choisis.includes(id)){ choisis.push(id); rendre(); i.value = ""; }
  };
  i.addEventListener("change", prendre);
  i.addEventListener("input", ()=>{ if(/· [^·]+$/.test(i.value)) prendre(); });
  w.append(puces, i, dl);
  w.valeurs = ()=>choisis;
  rendre();
  return w;
}

function editeur(cible, champs, o){
  fermerEditeur();
  const f = mk("form", {className:"editeur"});
  const entrees = {};
  champs.forEach(c=>{
    let i;
    if(c.type === "textarea")
      i = mk("textarea", {className:"saisie saisie-l", value:c.valeur||"", placeholder:c.aide||""});
    else if(c.type === "select"){
      i = mk("select", {className:"saisie"});
      c.options.forEach(([v,t])=>i.append(mk("option", {value:v, textContent:t})));
      i.value = c.valeur || "";
    }
    else if(c.type === "personnes") i = choixPersonnes(c.valeur||[]);
    else i = mk("input", {className:"saisie saisie-l", type:"text", value:c.valeur||"", placeholder:c.aide||""});
    entrees[c.nom] = i;
    f.append(mk("label", {className:"ed-champ"}, c.libelle ? mk("span", {textContent:c.libelle}) : null, i));
  });
  if(o.note) f.append(mk("p", {className:"ed-note", textContent:o.note}));
  const ok = mk("button", {type:"submit", className:"ed-ok", textContent:o.libelleOk || "Enregistrer"});
  const non = mk("button", {type:"button", className:"ed-non", textContent:"Annuler"});
  const boutons = mk("div", {className:"ed-boutons"}, ok, non);
  if(o.retirer){
    const r = mk("button", {type:"button", className:"ed-retirer", textContent:o.libelleRetirer || "Retirer"});
    r.onclick = ()=>{
      if(confirm(o.confirmer || "Retirer cet élément de la fiche ?\n\nIl reste consigné dans l'historique et peut être restauré."))
        o.retirer();
    };
    boutons.append(r);
  }
  f.append(boutons);
  const valeurs = ()=>{ const r = {}; for(const k in entrees){ const i = entrees[k];
    r[k] = i.valeurs ? i.valeurs() : i.value; } return r; };
  f.addEventListener("submit", e=>{ e.preventDefault(); o.enregistrer(valeurs()); });
  non.onclick = fermerEditeur;
  f.addEventListener("keydown", e=>{
    if(e.key === "Escape"){ e.preventDefault(); e.stopPropagation(); fermerEditeur(); }
    if(e.key === "Enter" && e.target.tagName === "INPUT" && !e.target.closest(".choix-pers")){
      e.preventDefault(); f.requestSubmit(); }
  });
  f.addEventListener("click", e=>e.stopPropagation());
  if(o.place === "apres"){ cible.hidden = true; cible.after(f); }
  else { cible.classList.add("en-edition"); cible.append(f); }
  ouvert = ()=>{ f.remove(); cible.hidden = false; cible.classList.remove("en-edition"); };
  const premier = f.querySelector("input, textarea, select");
  if(premier){ premier.focus(); if(premier.select && premier.value) premier.select(); }
  return f;
}

/* ===================================================================
   CHEMIN 1 — servie : chaque geste s'enregistre tout de suite.
   =================================================================== */
function envoyer(demande, recharger){
  demande.source = SOURCE;
  dire("Enregistrement…", "attente");
  return fetch("/_modifier", {method:"POST",
      headers:Object.assign({"Content-Type":"application/json", "X-Jeton":JETON}, EXTRA.entetes()),
      body:JSON.stringify(demande)})
    .then(r=>r.json())
    .then(o=>{
      if(!o || !o.ok){
        const e = (o && o.erreur) || "raison inconnue";
        dire("Non enregistré : " + e + EXTRA.indice(e), "erreur");
        return false;
      }
      if(o.inchange){ fermerEditeur(); dire("Rien n'a changé."); return true; }
      if(recharger === false) return true;
      apresEnregistrement(o.avertissement || (o.message.charAt(0).toUpperCase() + o.message.slice(1) + "."));
      return true;
    })
    .catch(()=>{
      dire("Le serveur ne répond plus : rien n'a été enregistré. Relancez Serveur_Local.bat.", "erreur");
      return false;
    });
}
function apresEnregistrement(message){
  /* Les données sont écrites et l'arbre est déjà refait quand le serveur
     répond : on recharge, à la même hauteur, et on prévient l'arbre ouvert
     dans un autre onglet pour qu'il se refasse aussi. */
  try { sessionStorage.setItem("apres-maj:" + PID, JSON.stringify({y:scrollY, msg:message})); } catch(e){}
  try { new BroadcastChannel("arbre-maj").postMessage({source:SOURCE, pid:PID}); } catch(e){}
  location.reload();
}

const EDITER = {
  fait(el){
    const v = val(el) || {}, cle = el.dataset.cle;
    editeur(el, [
      {nom:"texte", libelle:"Date et lieu", valeur:v.texte, aide:"jj-mm-aaaa, lieu — ou ce que vous savez"},
      {nom:"certitude", libelle:"Certitude", type:"select", options:CERTS, valeur:v.certitude},
      {nom:"note", libelle:"Note (facultative)", valeur:v.note, aide:"d'où vient l'information"}],
      {note: v.certitude === "attestee" ? EXTRA.noteAttestee : null,
       enregistrer: r=>envoyer({op:"fait", pid:PID, cle, texte:r.texte, certitude:r.certitude, note:r.note}),
       retirer: v.texte ? ()=>envoyer({op:"retrait", pid:PID, cle}) : null});
  },
  champ(el){
    const cle = el.dataset.cle, v = val(el);
    editeur(el, [{nom:"valeur", valeur:v}], {
      enregistrer: r=>envoyer({op:"champ", pid:PID, cle, valeur:r.valeur}),
      retirer: v ? ()=>envoyer({op:"retrait", pid:PID, cle}) : null});
  },
  liste(el){
    const champ = el.dataset.champ, i = +el.dataset.i, v = val(el);
    const long = champ === "notes" || champ === "marquants";
    editeur(el, [{nom:"valeur", type: long ? "textarea" : "texte", valeur:v}], {
      enregistrer: r=>envoyer({op:"liste", pid:PID, champ, index:i, attendu:v, valeur:r.valeur}),
      retirer: ()=>envoyer({op:"retrait", pid:PID, cle:champ, index:i, attendu:v})});
  },
  recette(el){
    const i = +el.dataset.i, v = val(el) || {};
    editeur(el, [
      {nom:"titre", libelle:"Nom de la recette", valeur:v.titre},
      {nom:"texte", libelle:"La recette", type:"textarea", valeur:v.texte,
       aide:"Ingrédients, préparation, et de qui elle vient…"}], {
      enregistrer: r=>envoyer({op:"recette", pid:PID, index:i, titre:r.titre, texte:r.texte}),
      retirer: ()=>envoyer({op:"recette", pid:PID, index:i, retrait:true}),
      libelleRetirer:"Retirer la recette"});
  },
  photo(el){
    const v = val(el) || {};
    editeur(el, [{nom:"legende", libelle:"Légende", valeur:v.legende, aide:"Qui, où, quand"}], {
      enregistrer: r=>envoyer({op:"photo", action:"legende", pid:PID, fichier:v.fichier, legende:r.legende}),
      retirer: ()=>envoyer({op:"photo", action:"retrait", pid:PID, fichier:v.fichier}),
      libelleRetirer:"Retirer la photo",
      confirmer:"Retirer cette photo de la fiche ?\n\nLe fichier n'est pas effacé : il est rangé dans photos/_retirees et peut être restauré."});
  },
  evenement(el){ editerEvenement(el, val(el) || {}); },
};

function editerEvenement(el, v, place){
  const nouveau = !v.id;
  editeur(el, [
    {nom:"date", libelle:"Quand", valeur:v.date, aide:"jj-mm-aaaa, une année, « vers 1975 »…"},
    {nom:"texte", libelle:"Ce qui s'est passé", type:"textarea", valeur:v.texte},
    {nom:"lieu", libelle:"Où (facultatif)", valeur:v.lieu},
    {nom:"personnes", libelle:"Personnes concernées", type:"personnes", valeur:v.personnes || [PID]},
    {nom:"certitude", libelle:"Certitude", type:"select", options:CERTS, valeur:v.certitude},
    /* « provenance » et non « source » : « source » désigne déjà le
       fichier de données dans chaque demande envoyée au serveur. */
    {nom:"provenance", libelle:"Source (facultative)", valeur:v.source, aide:"livre, page, témoignage de…"}], {
    place,
    libelleOk: nouveau ? "Ajouter" : "Enregistrer",
    note: "Un même fait apparaît sur la fiche de chaque personne concernée.",
    enregistrer: r=>envoyer(Object.assign({op:"evenement", id:v.id || null}, r)),
    retirer: nouveau ? null : ()=>envoyer({op:"evenement", id:v.id, retrait:true}),
    libelleRetirer:"Retirer ce fait"});
}

function poserCrayon(el, c){
  /* après la valeur, pas sous la note ni sous la légende */
  const sous = el.querySelector(".v > small, .v > figcaption");
  if(sous) sous.before(c); else el.append(c);
}
function brancherEdition(){
  document.body.classList.add("edition");
  $("#mode-note") && ($("#mode-note").textContent =
    "Cliquez sur une valeur pour la corriger : elle s'enregistre dans le projet et l'arbre se refait.");
  $$("[data-ed]").forEach(el=>{
    const f = EDITER[el.dataset.ed]; if(!f) return;
    const c = mk("button", {type:"button", className:"crayon", title:"Modifier", textContent:"✎"});
    c.setAttribute("aria-label", "Modifier");
    poserCrayon(el, c);
    el.addEventListener("click", e=>{
      if(el.classList.contains("en-edition") || e.target.closest(".editeur")) return;
      if(e.target.closest("a") && e.target !== c) return;     /* un lien reste un lien */
      e.preventDefault(); f(el);
    });
  });
  $$("[data-ajout-liste]").forEach(b=>b.addEventListener("click", ()=>{
    const champ = b.dataset.ajoutListe, long = champ === "notes" || champ === "marquants";
    editeur(b, [{nom:"valeur", type: long ? "textarea" : "texte"}], {place:"apres", libelleOk:"Ajouter",
      enregistrer: r=>envoyer({op:"liste", pid:PID, champ, index:null, valeur:r.valeur})});
  }));
  const bEv = $("#b-evenement");
  if(bEv) bEv.addEventListener("click", ()=>editerEvenement(bEv, {}, "apres"));
  $$("[data-retirer-section]").forEach(b=>b.addEventListener("click", ()=>{
    if(confirm("Retirer toute cette section de la fiche ?\n\nElle reste dans l'historique et peut être restaurée."))
      envoyer({op:"section_retrait", pid:PID, index:+b.dataset.retirerSection});
  }));
}

/* ===================================================================
   CHEMIN 2 — double-clic : on accumule, on rend un fichier.
   =================================================================== */
const AJOUTS = {id:PID, nom:PNOM, portrait:null, faits:{}, photos:[], recettes:[]};
const CLE = "ajouts:" + PID;
const pleine = rc => !!((rc.titre||"").trim() || (rc.texte||"").trim());

function compte(){
  /* Une recette vide n'est pas un ajout (défaut D-2) : elle ne compte pas,
     et elle ne part pas dans le fichier. */
  return (AJOUTS.portrait?1:0) + Object.keys(AJOUTS.faits).length
       + AJOUTS.photos.length + AJOUTS.recettes.filter(pleine).length;
}
function majBarre(){
  if(JETON) return;
  const n = compte();
  $("#barre").classList.toggle("visible", n>0);
  $("#quoi").textContent = n + (n>1 ? " ajouts en attente" : " ajout en attente");
  /* Filet de sécurité seulement : le vrai enregistrement est le fichier. */
  try { localStorage.setItem(CLE, JSON.stringify(AJOUTS)); } catch(e){}
}
function afficherFait(el, texte, enAttente){
  const v = el.querySelector(".v");
  v.textContent = texte || "non renseignée";
  v.classList.toggle("vide", !texte);
  if(enAttente) v.append(mk("span", {className:"en-attente", textContent:"en attente"}));
}
function editerFaitFichier(el){
  const v = val(el) || {}, cle = el.dataset.cle;
  editeur(el, [{nom:"texte", valeur: AJOUTS.faits[cle] || v.texte || "",
                aide:"jj-mm-aaaa, lieu — ou ce que vous savez"}], {
    libelleOk:"Garder",
    enregistrer: r=>{
      const t = r.texte.trim();
      fermerEditeur();
      /* Saisie vide ou inchangée : on rend la valeur d'origine, on ne la
         remplace jamais par « — » (défaut D-1). */
      if(!t || t === (v.texte||"")){ delete AJOUTS.faits[cle]; afficherFait(el, v.texte, false); }
      else { AJOUTS.faits[cle] = t; afficherFait(el, t, true); }
      majBarre();
    }});
}
function brancherFichier(){
  document.body.classList.add("ajouts");
  $$('[data-ed="fait"]').forEach(el=>{
    const c = mk("button", {type:"button", className:"crayon", title:"Modifier", textContent:"✎"});
    poserCrayon(el, c);
    el.addEventListener("click", e=>{
      if(el.classList.contains("en-edition") || e.target.closest(".editeur")) return;
      if(e.target.closest("a") && e.target !== c) return;
      e.preventDefault(); editerFaitFichier(el);
    });
  });
}
function rendrePhotos(){
  const h = $("#liste-photos");
  h.innerHTML = "";
  AJOUTS.photos.forEach((ph,k)=>{
    const d = mk("div", {className:"vignette"});
    d.append(mk("img", {src:ph.donnee, alt:""}));
    const lg = mk("input", {className:"saisie saisie-l", placeholder:"Légende", value:ph.legende||""});
    lg.style.marginTop = "7px"; lg.style.fontSize = "12.5px";
    lg.addEventListener("input", ()=>{ ph.legende = lg.value; majBarre(); });
    const x = mk("button", {type:"button", className:"b-petit", textContent:"Retirer"});
    x.onclick = ()=>{ AJOUTS.photos.splice(k,1); rendrePhotos(); majBarre(); };
    d.append(lg, x); h.append(d);
  });
}
function rendreRecettes(){
  const h = $("#liste-recettes");
  h.innerHTML = "";
  AJOUTS.recettes.forEach((rc,k)=>{
    const d = mk("div", {className:"recette"});
    const ti = mk("input", {className:"saisie saisie-l", placeholder:"Nom de la recette", value:rc.titre});
    ti.addEventListener("input", ()=>{ rc.titre = ti.value; majBarre(); });
    const tx = mk("textarea", {className:"saisie saisie-l",
      placeholder:"Ingrédients, préparation, et de qui elle vient…", value:rc.texte});
    tx.addEventListener("input", ()=>{ rc.texte = tx.value; majBarre(); });
    const x = mk("button", {type:"button", className:"b-petit", textContent:"Retirer cette recette"});
    x.onclick = ()=>{ AJOUTS.recettes.splice(k,1); rendreRecettes(); majBarre(); };
    d.append(ti, tx, x); h.append(d);
  });
}
function parFichier(){
  const envoi = Object.assign({}, AJOUTS, {recettes: AJOUTS.recettes.filter(pleine)});
  const b = new Blob([JSON.stringify(envoi, null, 1)], {type:"application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(b); a.download = "ajouts-" + PID + ".json";
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href), 4000);
  $("#quoi").textContent = "Fichier rendu. Déposez-le sur Appliquer_Ajouts.bat.";
}
$("#b-enregistrer").addEventListener("click", ()=>{
  AJOUTS.date = new Date().toISOString().slice(0,10);
  parFichier();
});

/* ===================================================================
   Les gestes communs aux deux chemins : portrait, photos, recettes.
   =================================================================== */
const zone = $("#zone-portrait"), fPortrait = $("#f-portrait"), fPhotos = $("#f-photos");
if(zone){
  zone.addEventListener("click", ()=>fPortrait.click());
  zone.addEventListener("keydown", e=>{ if(e.key==="Enter"||e.key===" "){ e.preventDefault(); fPortrait.click(); } });
}
fPortrait.addEventListener("change", ()=>{
  const f = fPortrait.files[0]; if(!f) return;
  lire(f, d=>{
    if(JETON){ envoyer({op:"portrait", pid:PID, donnee:d}); return; }
    zone.innerHTML = '<img class="portrait" alt="">';
    zone.querySelector("img").src = d;
    AJOUTS.portrait = {fichier:f.name, donnee:d};
    const avis = $("#sans-portrait"); if(avis) avis.remove();
    majBarre();
  });
  fPortrait.value = "";
});
$("#b-photos").addEventListener("click", ()=>fPhotos.click());
fPhotos.addEventListener("change", ()=>{
  const fichiers = [...fPhotos.files];
  fPhotos.value = "";
  if(!JETON){
    fichiers.forEach(f=>lire(f, d=>{
      AJOUTS.photos.push({fichier:f.name, donnee:d, legende:""});
      rendrePhotos(); majBarre();
    }));
    return;
  }
  /* Servie : les photos partent une à une, puis on recharge une fois. */
  let n = 0;
  (function suivante(){
    if(n >= fichiers.length){
      apresEnregistrement(n > 1 ? n + " photos ajoutées." : "Photo ajoutée.");
      return;
    }
    const f = fichiers[n];
    dire("Envoi de la photo " + (n+1) + " sur " + fichiers.length + "…", "attente");
    lire(f, d=>envoyer({op:"photo", action:"ajout", pid:PID, donnee:d, legende:""}, false)
      .then(ok=>{ if(ok){ n++; suivante(); } }));
  })();
});
$("#b-recette").addEventListener("click", ()=>{
  if(JETON){
    const b = $("#b-recette");
    editeur(b, [
      {nom:"titre", libelle:"Nom de la recette"},
      {nom:"texte", libelle:"La recette", type:"textarea", aide:"Ingrédients, préparation, et de qui elle vient…"}], {
      place:"apres", libelleOk:"Ajouter la recette",
      enregistrer: r=>envoyer({op:"recette", pid:PID, index:null, titre:r.titre, texte:r.texte})});
    return;
  }
  AJOUTS.recettes.push({titre:"", texte:""}); rendreRecettes(); majBarre();
  const t = $$("#liste-recettes .recette .saisie").slice(-2)[0]; if(t) t.focus();
});

/* ===================================================================
   Au chargement : quel chemin ?
   =================================================================== */
function demarrerFichier(){
  brancherFichier();
  try {
    const vieux = localStorage.getItem(CLE);
    if(vieux){
      Object.assign(AJOUTS, JSON.parse(vieux));
      AJOUTS.recettes = (AJOUTS.recettes||[]).filter(pleine);
      if(AJOUTS.portrait && zone){
        zone.innerHTML = '<img class="portrait" alt="">';
        zone.querySelector("img").src = AJOUTS.portrait.donnee;
      }
      Object.entries(AJOUTS.faits||{}).forEach(([cle,v])=>{
        const el = $('[data-ed="fait"][data-cle="'+cle+'"]');
        if(el) afficherFait(el, v, true);
      });
      rendrePhotos(); rendreRecettes(); majBarre();
    }
  } catch(e){}
}
if(SERVIE){
  fetch("/_jeton").then(r=>r.ok ? r.json() : null).then(o=>{
    if(o && o.jeton){
      JETON = o.jeton;
      brancherEdition();
      EXTRA.apresChargement(o);
      try {
        const m = JSON.parse(sessionStorage.getItem("apres-maj:" + PID) || "null");
        if(m){ sessionStorage.removeItem("apres-maj:" + PID); scrollTo(0, m.y||0); dire(m.msg, m.msg && /échoué/.test(m.msg) ? "erreur" : ""); }
      } catch(e){}
    } else demarrerFichier();
  }).catch(demarrerFichier);
} else demarrerFichier();
document.addEventListener("keydown", e=>{ if(e.key==="Escape") fermerEditeur(); });
</script>
__ADMIN_JS__
<script>
document.querySelectorAll(".voile button").forEach(b=>b.addEventListener("click",()=>{
  const v=b.closest(".voile"), c=v.querySelector(".voile-contenu");
  const o=v.getAttribute("data-ouvert")==="1";
  v.setAttribute("data-ouvert", o?"0":"1"); c.hidden=o;
  b.firstChild.nodeValue = o ? "Contenu confidentiel — cliquer pour afficher"
                             : "Contenu confidentiel — cliquer pour masquer";
}));
</script>
</body>
</html>
"""

SCRIPT_ADMIN = r"""<style>
.admin-seul{display:none}
body.admin .admin-seul{display:revert}
.b-adm{font:inherit; border-radius:7px; cursor:pointer; margin-left:auto; border:1px solid var(--line); background:transparent; color:var(--muted); font-size:12px; padding:4px 11px}
.b-adm.actif{border-color:var(--alerte); color:var(--alerte); background:var(--alerte-bg); font-weight:600}
dialog#d-adm{border:1px solid var(--line); border-radius:12px; background:var(--surface); color:var(--ink);
  padding:20px 22px; width:min(380px, calc(100vw - 32px))}
dialog#d-adm::backdrop{background:color-mix(in srgb, var(--ink) 40%, transparent)}
dialog#d-adm h3{margin:0 0 6px; font-size:17px}
dialog#d-adm p{font-size:13px; color:var(--muted); margin:0 0 12px; line-height:1.5}
dialog#d-adm .saisie{width:100%; min-width:0; margin:0 0 6px}
ol.historique{list-style:none; margin:0; padding:0}
.hist{padding:8px 0; border-bottom:1px solid var(--line-soft); font-size:13.4px; line-height:1.5}
.hist-d{color:var(--faint); font-variant-numeric:tabular-nums; margin-right:9px; font-size:12px}
.hist-adm{font-size:10px; font-weight:700; color:var(--alerte); background:var(--alerte-bg);
  padding:1px 6px; border-radius:4px; margin-left:7px}
.hist-v{display:block; color:var(--muted); font-size:12.6px}
</style>
<script>
"use strict";
/* ===================================================================
   MODE ADMINISTRATEUR — C-021. Absent de la version partageable.

   La page ne connaît PAS le mot de passe : elle l'envoie au serveur local,
   qui le compare à une empreinte gardée hors de git et rend un jeton de
   session. Sans serveur, ce mode n'existe pas.

   Ce qu'il ouvre : remplacer un fait attesté, changer un nom, retirer ce
   qui vient des sources, et restaurer depuis l'historique. Rien n'est
   jamais effacé : chaque retrait est consigné et réversible.
   =================================================================== */
let SESSION_ADM = null;
try { SESSION_ADM = localStorage.getItem("session-adm"); } catch(e){}
const bAdm = $("#b-adm"), dAdm = $("#d-adm");

EXTRA.entetes = ()=> SESSION_ADM ? {"X-Admin": SESSION_ADM} : {};
EXTRA.noteAttestee = "Fait attesté par la source : seul le mode administrateur peut le remplacer. "
  + "L'ancienne valeur reste dans l'historique.";
EXTRA.indice = e => (/administrateur/.test(e) && !SESSION_ADM) ? " (bouton « Administrateur » en haut de la page)" : "";
EXTRA.apresChargement = o=>{
  if(!o.admin_possible) return;
  bAdm.hidden = false;
  if(SESSION_ADM) chargerHistorique();
  majAdm();
};

function majAdm(){
  document.body.classList.toggle("admin", !!SESSION_ADM);
  bAdm.textContent = SESSION_ADM ? "Administrateur · quitter" : "Administrateur";
  bAdm.classList.toggle("actif", !!SESSION_ADM);
}
function oublier(){
  SESSION_ADM = null;
  try { localStorage.removeItem("session-adm"); } catch(e){}
  majAdm();
}
function poster(chemin, corps){
  return fetch(chemin, {method:"POST", headers:Object.assign(
    {"Content-Type":"application/json", "X-Jeton":JETON}, EXTRA.entetes()),
    body:JSON.stringify(corps||{})}).then(r=>r.json());
}
bAdm.addEventListener("click", ()=>{
  if(SESSION_ADM){
    poster("/_admin_sortir").catch(()=>{});
    oublier(); dire("Mode administrateur quitté.");
    return;
  }
  $("#adm-mdp").value = ""; $("#adm-err").textContent = "";
  dAdm.showModal();
});
$("#adm-non").addEventListener("click", ()=>dAdm.close());
$("#adm-form").addEventListener("submit", e=>{
  e.preventDefault();
  $("#adm-err").textContent = "Vérification…";
  poster("/_admin", {motdepasse: $("#adm-mdp").value}).then(o=>{
    if(o && o.ok){
      SESSION_ADM = o.admin;
      try { localStorage.setItem("session-adm", SESSION_ADM); } catch(e){}
      dAdm.close(); majAdm(); chargerHistorique();
      dire("Mode administrateur ouvert.");
    } else $("#adm-err").textContent = (o && o.erreur) || "refusé";
  }).catch(()=>{ $("#adm-err").textContent = "Le serveur ne répond pas."; });
});

const LIB_ACTION = {ajout:"ajouté", modification:"modifié", retrait:"retiré", restauration:"restauré"};
function court(x){
  if(x == null || x === "") return "—";
  if(typeof x === "string") return x.length > 90 ? x.slice(0,89) + "…" : x;
  if(x.texte) return court(x.texte + (x.date ? " (" + x.date + ")" : ""));
  if(x.titre) return court(x.titre);
  return court(JSON.stringify(x));
}
function chargerHistorique(){
  poster("/_historique", {source:SOURCE, pid:PID}).then(o=>{
    if(!o || !o.ok){ oublier(); return; }
    const h = $("#liste-historique"); h.textContent = "";
    const entrees = (o.entrees||[]).slice().reverse();
    if(!entrees.length){ h.append(mk("p", {className:"src", textContent:"Aucune modification consignée pour cette fiche."})); return; }
    entrees.forEach(e=>{
      const li = mk("li", {className:"hist"});
      li.append(mk("span", {className:"hist-d", textContent:(e.date||"").replace("T"," ").slice(0,16)}),
        mk("b", {textContent:(e.champ||"") + " " + (LIB_ACTION[e.action]||e.action||"")}),
        e.admin ? mk("span", {className:"hist-adm", textContent:"admin"}) : null);
      if(e.ancien != null) li.append(mk("span", {className:"hist-v", textContent:"avant : " + court(e.ancien)}));
      if(e.nouveau != null) li.append(mk("span", {className:"hist-v", textContent:"après : " + court(e.nouveau)}));
      if(e.restauree) li.append(mk("span", {className:"hist-v", textContent:"restauré le " + e.restauree.replace("T"," ").slice(0,16)}));
      else if((e.action === "retrait" || e.action === "modification") && e.ancien != null){
        const b = mk("button", {type:"button", className:"b-petit",
          textContent: e.action === "retrait" ? "Restaurer" : "Revenir à l'ancienne valeur"});
        b.onclick = ()=>envoyer({op:"restaurer", n:e.n});
        li.append(b);
      }
      h.append(li);
    });
  }).catch(()=>{});
}
</script>
"""

LIB_CERT = {"approximative": "approx.", "deduite": "déduit", "divergente": "divergent",
            "incoherente": "incohérent", "inconnue": "inconnu"}


def esc(s):
    return (str("" if s is None else s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def nom_complet(p):
    # « nom_affiche » l'emporte : en vietnamien le nom précède le prénom.
    return (p.get("nom_affiche")
            or ((p.get("prenom") or "") + " " + (p.get("nom") or ""))).strip()


def initiales(p):
    a = (p.get("prenom") or "?").strip()[:1] or "?"
    b = (p.get("nom") or "").strip()[:1]
    return (a + b).upper()


def _an(f):
    if not f:
        return None
    if isinstance(f.get("tri"), int):
        return f["tri"]
    import re as _re
    m = _re.search(r"(1[5-9]\d{2})", f.get("texte", "") or "")
    return int(m.group(1)) if m else None


def vie(p):
    fn = p.get("naissance") if _an(p.get("naissance")) else p.get("bapteme")
    fd = p.get("deces") if _an(p.get("deces")) else p.get("sepulture")
    n, d = _an(fn), _an(fd)
    ap = lambda f: bool(f) and f.get("certitude") in ("approximative", "deduite")
    g = "~" if ap(fn) else ""
    h = "~" if ap(fd) else ""
    if n and d:
        return f"{g}{n} – {h}{d}"
    if n:
        return f"{g}{n} –"
    if d:
        return f"– {h}{d}"
    return ""


def cert_html(x):
    c = (x or {}).get("certitude")
    if not c or c == "attestee":
        return ""
    return f'<span class="marque-cert c-{c}">{LIB_CERT.get(c, c)}</span>'


def nettoyer_lieu(t):
    import re as _re
    t = _re.sub(r"\([^)]*\)", " ", str(t or ""))
    t = _re.sub(r"\s{2,}", " ", t).strip()
    return t.strip(" ,;")


def url_carte(texte, carte):
    """Lien cartographique pour un lieu, ou None.
    La table meta.carte.lieux prime ; une valeur vide désactive le lien."""
    if not carte or carte.get("actif") is False:
        return None
    from urllib.parse import quote
    table = carte.get("lieux") or {}
    q = table[texte] if texte in table else nettoyer_lieu(texte)
    if not q:
        return None
    service = carte.get("service") or "https://www.google.com/maps/search/?api=1&query="
    return service + quote(q)


def lieu_html(texte, carte):
    u = url_carte(texte, carte)
    if not u:
        return esc(texte)
    return (f'<a class="lieu" href="{esc(u)}" target="_blank" rel="noopener" '
            f'title="Voir sur la carte">{esc(texte)}</a>')


def _aplatir(t):
    return t.replace("\u2019", "'").lower()


def _est_lettre(c):
    import re as _re
    return bool(c) and bool(_re.match(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ'\u2019]", c))


def lier_lieux(txt, carte):
    """Reconnaît les toponymes dans un texte DÉJÀ ÉCHAPPÉ et les rend cliquables.
    Une seule occurrence par nom et par bloc, pour ne pas surcharger la lecture."""
    if not carte or carte.get("actif") is False or not txt:
        return txt
    from urllib.parse import quote
    topo = {k: v for k, v in (carte.get("toponymes") or {}).items() if v}
    if not topo:
        return txt
    service = carte.get("service") or "https://www.google.com/maps/search/?api=1&query="
    res = str(txt)
    pris = []
    for nom in sorted(topo, key=len, reverse=True):
        cible = _aplatir(nom)
        n = len(cible)
        depart, i = 0, -1
        while True:
            i = _aplatir(res).find(cible, depart)
            if i < 0:
                break
            dans_balise = res.rfind("<", 0, i + 1) > res.rfind(">", 0, i + 1)
            chevauche = any(i < b and i + n > a for a, b in pris)
            avant = res[i - 1] if i > 0 else ""
            apres = res[i + n] if i + n < len(res) else ""
            if not _est_lettre(avant) and not _est_lettre(apres) and not dans_balise and not chevauche:
                break
            depart = i + 1
        if i < 0:
            continue
        brut = res[i:i + n]
        a = (f'<a class="lieu" href="{service}{quote(topo[nom])}" target="_blank" '
             f'rel="noopener" title="Voir sur la carte">{brut}</a>')
        res = res[:i] + a + res[i + n:]
        d = len(a) - n
        pris = [[x + d, y + d] if x > i else [x, y] for x, y in pris]
        pris.append([i, i + len(a)])
    return res


def tl(txt, carte):
    """Échappe puis enrichit de liens de lieux."""
    return lier_lieux(esc(txt), carte)


def lien(pid, personnes, texte=None):
    p = personnes.get(pid)
    if not p:
        return esc(pid)
    return f'<a href="{esc(pid)}.html">{esc(texte or nom_complet(p))}</a>'


def section_page_html(s, carte=None):
    t = s.get("type") or ("liste" if isinstance(s.get("contenu"), list) else "texte")
    c = s.get("contenu")
    # Les sections confidentielles ne sont jamais parcourues pour y chercher
    # des lieux : une adresse privée n'a pas à devenir une requête Google.
    T = (lambda x: esc(x)) if s.get("prive") else (lambda x: tl(x, carte))
    h = f'<p class="intro">{esc(s["intro"])}</p>' if s.get("intro") else ""
    if t == "texte":
        items = c if isinstance(c, list) else [c]
        h += '<div class="texte">' + "".join(f"<p>{T(x)}</p>" for x in items) + "</div>"
    elif t == "liste":
        h += '<ul class="puces">' + "".join(f"<li>{T(x)}</li>" for x in (c or [])) + "</ul>"
    elif t == "faits":
        h += '<dl class="faits">' + "".join(
            f'<dt>{esc(f.get("q",""))}</dt><dd>{T(f.get("r",""))}{cert_html(f)}'
            + (f'<small>{T(f["note"])}</small>' if f.get("note") else "") + "</dd>"
            for f in (c or [])) + "</dl>"
    elif t == "chrono":
        h += '<ol class="chrono">' + "".join(
            f'<li><span class="d">{esc(e.get("date",""))}</span>'
            f'<span class="t">{T(e.get("titre",""))}</span>'
            + (f'<span class="x">{T(e["detail"])}</span>' if e.get("detail") else "")
            + (f'<span class="x">{lieu_html(e["lieu"], carte)}</span>' if e.get("lieu") else "")
            + "</li>"
            for e in (c or [])) + "</ol>"
    elif t == "tableau":
        col = (c or {}).get("colonnes", [])
        lig = (c or {}).get("lignes", [])
        h += ("<table><thead><tr>" + "".join(f"<th>{esc(x)}</th>" for x in col)
              + "</tr></thead><tbody>"
              + "".join("<tr>" + "".join(f"<td>{T(x)}</td>" for x in (r or [])) + "</tr>" for r in lig)
              + "</tbody></table>")
    else:
        h += f"<p>{esc(c)}</p>"
    if s.get("source"):
        h += f'<p class="src" style="margin-top:11px">{esc(s["source"])}</p>'
    return h


def attr_json(o):
    """Une valeur pour un attribut data-val : JSON, puis échappée."""
    return esc(json.dumps(o, ensure_ascii=False))


def est_recette(s):
    return bool(s.get("recette")) or str(s.get("titre", "")).startswith("Recette — ")


def titre_recette(s):
    t = str(s.get("titre", ""))
    return t[len("Recette — "):] if t.startswith("Recette — ") else t


def evenements_de(pid, donnees):
    evs = [e for e in donnees.get("evenements", []) if pid in (e.get("personnes") or [])]
    return sorted(evs, key=lambda e: (e.get("tri") or 9999, e.get("date") or ""))


def construire_page(pid, donnees, nom_arbre, date_gen, source_nom="", partage=False,
                    galerie=None, personnes_js="[]"):
    personnes = donnees["personnes"]
    p = personnes[pid]
    unions = donnees.get("unions", [])
    mes_unions = [u for u in unions if pid in u.get("conjoints", [])]
    union_parente = next((u for u in unions if pid in (u.get("enfants") or [])), None)
    carte = donnees.get("meta", {}).get("carte")
    admin_ok = not partage      # la version partageable ne porte aucune trace du mode

    # ---- bandeaux d'identité ----
    # Même règle que sur la carte flottante : pas de champ, pas de jeton.
    jetons = ('<span class="jeton j-nf">Nouvelle-France</span>' if p.get("pays") == "nf"
              else '<span class="jeton j-fr">France</span>' if p.get("pays") == "fr"
              else "")
    if p.get("ancetre"):
        jetons += '<span class="jeton j-or">Ancêtre canadien</span>'
    elif p.get("lignee"):
        jetons += '<span class="jeton j-or">Lignée directe</span>'
    if p.get("lacune"):
        jetons += '<span class="jeton j-al">Rattachement non documenté</span>'
    if any(s.get("prive") for s in p.get("sections", [])):
        jetons += '<span class="jeton j-al">Contient du confidentiel</span>'

    # Le portrait est une zone cliquable, avec ou sans image : on remplace
    # aussi bien qu'on ajoute. Le titre dit ce qui va se passer, parce qu'un
    # rond cliquable sans libellé ne se devine pas.
    dedans = (f'<img class="portrait" src="{p["_photo"]}" alt="">' if p.get("_photo")
              else f'<div class="mono">{esc(initiales(p))}</div>')
    portrait = ('<div class="zone-portrait" id="zone-portrait" role="button" tabindex="0" '
                'title="Cliquer pour choisir une photo sur cet ordinateur">'
                + dedans + "</div>")
    v = vie(p)
    dates = f'<p class="dates">{esc(v)}</p>' if v else ""
    surnom = f'<p class="surnom">{esc(p["surnom"])}</p>' if p.get("surnom") else ""

    corps, cote = [], []

    def ajoute(ancre, titre, contenu, vide=False, classe=""):
        """« vide » : la rubrique n'a rien encore ; elle n'apparaît qu'en
        modification, pour qu'on puisse la remplir."""
        if not contenu:
            return
        cl = " ".join(x for x in (classe, "vide-edition" if vide else "") if x)
        cla = f' class="{cl}"' if cl else ""
        corps.append(f'<section id="{ancre}"{cla}><h2>{esc(titre)}</h2>{contenu}</section>')
        cote.append(f'<a href="#{ancre}"{cla}>{esc(titre)}</a>')

    def liste_ed(champ, items, rendu, libelle_ajout):
        lis = "".join(f'<li class="ed" data-ed="liste" data-champ="{champ}" data-i="{i}" '
                      f'data-val="{attr_json(x)}"><span class="v">{rendu(x)}</span></li>'
                      for i, x in enumerate(items))
        return (f'<ul class="liste-ed l-{champ}">{lis}</ul>'
                f'<button type="button" class="b-plus-ed" data-ajout-liste="{champ}">'
                f'+ {esc(libelle_ajout)}</button>')

    # ---- synthèse ----
    # Chaque valeur porte de quoi la modifier : data-ed dit quoi, data-val
    # ce qui est là. L'éditeur part de la valeur RÉELLE (défaut D-1 : la
    # boîte s'ouvrait vide parce qu'elle ne connaissait que les ajouts).
    L = []
    for lib, cle in (("Naissance", "naissance"), ("Baptême", "bapteme"),
                     ("Décès", "deces"), ("Sépulture", "sepulture")):
        x = p.get(cle)
        if x:
            val = {"texte": x.get("texte", ""), "certitude": x.get("certitude") or "",
                   "note": x.get("note") or ""}
            dedans = (f'<span class="v">{tl(x.get("texte","—"), carte)}{cert_html(x)}'
                      + (f'<small>{tl(x["note"], carte)}</small>' if x.get("note") else "")
                      + "</span>")
            L.append(f'<dt>{lib}</dt><dd class="ed" data-ed="fait" data-cle="{cle}" '
                     f'data-val="{attr_json(val)}">{dedans}</dd>')
        else:
            # Même sans date connue, la ligne de naissance existe : sinon il
            # n'y a rien où cliquer. Les autres n'apparaissent qu'en
            # modification.
            cl = "" if cle == "naissance" else ' class="vide-edition"'
            L.append(f'<dt{cl}>{lib}</dt><dd{cl} data-ed="fait" data-cle="{cle}" data-val="null">'
                     f'<span class="v vide">non renseignée</span></dd>')
    if admin_ok:
        for lib, cle in (("Prénom", "prenom"), ("Nom", "nom"), ("Nom affiché", "nom_affiche")):
            L.append(f'<dt class="admin-seul">{lib}</dt><dd class="admin-seul ed" data-ed="champ" '
                     f'data-cle="{cle}" data-val="{attr_json(p.get(cle))}">'
                     f'<span class="v">{esc(p.get(cle) or "—")}</span></dd>')
    cl = "" if p.get("surnom") else ' class="vide-edition"'
    L.append(f'<dt{cl}>Surnom</dt><dd{cl} data-ed="champ" data-cle="surnom" '
             f'data-val="{attr_json(p.get("surnom"))}"><span class="v{"" if p.get("surnom") else " vide"}">'
             f'{esc(p.get("surnom") or "aucun")}</span></dd>')
    for lib, champ, rendu, aj in (("Variantes", "variantes", esc, "variante"),
                                  ("Métier", "metiers", esc, "métier"),
                                  ("Lieux", "lieux", lambda m: lieu_html(m, carte), "lieu")):
        items = p.get(champ) or []
        cl = "" if items else ' class="vide-edition"'
        L.append(f"<dt{cl}>{lib}</dt><dd{cl}>" + liste_ed(champ, items, rendu, aj) + "</dd>")
    ajoute("synthese", "Synthèse", f'<dl class="faits">{"".join(L)}</dl>'
           '<p class="note-ajout" id="mode-note"></p>')

    # ---- faits marquants ----
    # Deux origines, une seule rubrique : les faits rattachés à plusieurs
    # personnes (donnees.evenements, C-021) et les mentions lues dans les
    # sources (p.marquants), qui restent des phrases.
    evs = evenements_de(pid, donnees)
    M = []
    for e in evs:
        autres = [x for x in e.get("personnes", []) if x != pid]
        avec = ("<small>avec " + ", ".join(lien(x, personnes) for x in autres) + "</small>"
                if autres else "")
        M.append(f'<li class="ed ev" data-ed="evenement" data-val="{attr_json(e)}"><span class="v">'
                 + (f'<span class="ev-date">{esc(e["date"])}</span>' if e.get("date") else "")
                 + tl(e.get("texte", ""), carte) + cert_html(e)
                 + (f'<small>{lieu_html(e["lieu"], carte)}</small>' if e.get("lieu") else "")
                 + avec
                 + (f'<small class="ev-src">{esc(e["source"])}</small>' if e.get("source") else "")
                 + "</span></li>")
    for i, m in enumerate(p.get("marquants") or []):
        M.append(f'<li class="ed" data-ed="liste" data-champ="marquants" data-i="{i}" '
                 f'data-val="{attr_json(m)}"><span class="v">{tl(m, carte)}</span></li>')
    ajoute("marquants", "Faits marquants",
           f'<ul class="marquants">{"".join(M)}</ul>'
           '<button type="button" class="b-plus-ed" id="b-evenement">+ Ajouter un fait marquant</button>',
           vide=not M)

    # ---- notes ----
    notes = p.get("notes") or []
    ajoute("notes", "Notes", liste_ed("notes", notes, lambda m: tl(m, carte), "note")
           .replace('class="liste-ed l-notes"', 'class="liste-ed l-notes puces"'),
           vide=not notes)

    # ---- sections versées ----
    # Les recettes ont leur rubrique à elles, plus bas ; les autres sections
    # restent telles que versées, et seul l'administrateur peut en retirer.
    for i, s in enumerate(p.get("sections", [])):
        if est_recette(s):
            continue
        inner = section_page_html(s, carte)
        if s.get("prive"):
            inner = ('<div class="voile" data-ouvert="0"><button type="button">'
                     "Contenu confidentiel — cliquer pour afficher"
                     "<span>Masqué par défaut, et absent de la version partageable.</span>"
                     f'</button><div class="voile-contenu" hidden>{inner}</div></div>')
        if admin_ok:
            inner += (f'<button type="button" class="b-petit admin-seul" '
                      f'data-retirer-section="{i}">Retirer cette section</button>')
        ajoute(f"s{i}", s.get("titre") or f"Section {i+1}", inner)

    # ---- relations ----
    R = []
    if union_parente:
        R.append("<dt>Parents</dt><dd>"
                 + " &amp; ".join(lien(c, personnes) for c in union_parente["conjoints"]) + "</dd>")
        fratrie = [e for e in (union_parente.get("enfants") or []) if e != pid]
        if fratrie:
            R.append("<dt>Fratrie</dt><dd>"
                     + ", ".join(lien(e, personnes, (personnes.get(e) or {}).get("prenom")) for e in fratrie)
                     + "</dd>")
    for u in mes_unions:
        autre = next((c for c in u["conjoints"] if c != pid), None)
        det = []
        if u.get("mariage"):
            det.append("mariage : " + esc(u["mariage"]["texte"]))
        if u.get("contrat"):
            det.append("contrat : " + esc(u["contrat"]["texte"]))
        for n in (u.get("notes") or []):
            det.append(esc(n))
        R.append("<dt>Union</dt><dd>" + (lien(autre, personnes) if autre else "—")
                 + "".join(f'<small style="display:block;color:var(--muted);font-size:12.6px;'
                           f'line-height:1.45;margin-top:3px">{d}</small>' for d in det) + "</dd>")
        enfants = u.get("enfants") or []
        if enfants:
            R.append("<dt>Enfants</dt><dd>"
                     + ", ".join(lien(e, personnes, (personnes.get(e) or {}).get("prenom")) for e in enfants)
                     + "</dd>")
    ajoute("relations", "Relations", f'<dl class="rel">{"".join(R)}</dl>' if R else "")

    # ---- photos et recettes : toujours là, même vides ----
    # Une rubrique vide n'est pas un manque : c'est une invitation.
    V = []
    for g in (galerie or []):
        V.append(f'<figure class="vignette ed" data-ed="photo" '
                 f'data-val="{attr_json({"fichier": g["fichier"], "legende": g.get("legende") or ""})}">'
                 f'<span class="v"><img src="{g["uri"]}" alt="{esc(g.get("legende") or "")}">'
                 + (f'<figcaption>{esc(g["legende"])}</figcaption>' if g.get("legende") else "")
                 + "</span></figure>")
    ajoute("photos", "Photos",
           f'<div class="vignettes">{"".join(V)}</div>'
           '<div class="vignettes" id="liste-photos"></div>'
           '<button type="button" class="b-ajout" id="b-photos">'
           '+ Ajouter des photos</button>'
           '<p class="note-ajout note-fichier">Les photos choisies s\'affichent tout de suite. '
           'Ouverte depuis <code>Serveur_Local.bat</code>, cette fiche les range '
           'directement dans le projet ; ouverte par double-clic, elle rend un '
           'fichier d\'ajouts à déposer sur <code>Appliquer_Ajouts.bat</code>.</p>')
    RC = []
    for i, s in enumerate(p.get("sections", [])):
        if not est_recette(s):
            continue
        c = s.get("contenu")
        texte = "\n\n".join(c) if isinstance(c, list) else str(c or "")
        RC.append(f'<div class="recette ed" data-ed="recette" data-i="{s.get("_i", i)}" '
                  f'data-val="{attr_json({"titre": titre_recette(s), "texte": texte})}">'
                  f'<div class="v"><h3>{esc(titre_recette(s))}</h3><p>{esc(texte)}</p>'
                  + (f'<small class="src">{esc(s["source"])}</small>' if s.get("source") else "")
                  + "</div></div>")
    ajoute("recettes", "Recettes",
           "".join(RC) + '<div id="liste-recettes"></div>'
           '<button type="button" class="b-ajout" id="b-recette">'
           '+ Ajouter une recette</button>')

    # ---- points à vérifier ----
    pbs = [x for x in donnees.get("problemes", []) if pid in (x.get("personnes") or [])]
    if pbs:
        ajoute("verifier", "À vérifier", "".join(
            f'<div class="avis"><b>{esc(x.get("type",""))} — p. {esc(x.get("pages","?"))}</b><br>'
            f'{tl(x.get("description",""), carte)}</div>' for x in pbs))

    # ---- sources ----
    if p.get("sources"):
        ajoute("sources", "Source", f'<p class="src">{esc(" · ".join(p["sources"]))}</p>')

    # ---- historique : administrateur seulement, rempli par le serveur ----
    if admin_ok:
        ajoute("historique", "Historique des modifications",
               '<ol class="historique" id="liste-historique"></ol>', classe="admin-seul")

    if not p.get("_photo"):
        corps.append('<p class="src" id="sans-portrait">Pas encore de portrait. '
                     "Cliquez sur le rond en haut de la page pour en choisir un sur "
                     "cet ordinateur — ou déposez une image nommée "
                     f'<code>{esc(pid)}.jpg</code> dans le dossier <code>photos</code>.</p>')

    meta = donnees.get("meta", {})
    pied = (f'Fiche générée le {date_gen} à partir de <strong>{esc(meta.get("titre",""))}</strong>. '
            "Les mentions « approx. », « déduit », « divergent » et « incohérent » signalent ce que la "
            "source ne garantit pas. Rien n'a été complété par recherche extérieure.")

    bouton_admin = ('<button type="button" class="b-adm" id="b-adm" hidden>Administrateur</button>'
                    if admin_ok else "")
    dialogue_admin = ('<dialog id="d-adm"><form id="adm-form">'
                      '<h3>Mode administrateur</h3>'
                      '<p>Remplacer un fait attesté, retirer ce qui n\'a pas sa place, '
                      'restaurer depuis l\'historique.</p>'
                      '<input type="password" id="adm-mdp" class="saisie" '
                      'autocomplete="current-password" placeholder="Mot de passe">'
                      '<p class="ed-note" id="adm-err"></p>'
                      '<div class="ed-boutons"><button type="submit" class="ed-ok">Entrer</button>'
                      '<button type="button" class="ed-non" id="adm-non">Annuler</button></div>'
                      '</form></dialog>' if admin_ok else "")

    return (GABARIT_PAGE
            .replace("__ADMIN_JS__", SCRIPT_ADMIN if admin_ok else "")
            .replace("__DIALOGUE_ADMIN__", dialogue_admin)
            .replace("__BOUTON_ADMIN__", bouton_admin)
            .replace("__PERSONNES__", personnes_js)
            .replace("__SOURCE__", esc(source_nom))
            .replace("__COTE__", "".join(cote))
            .replace("__CORPS__", "".join(corps))
            .replace("__PORTRAIT__", portrait)
            .replace("__DATES__", dates)
            .replace("__SURNOM__", surnom)
            .replace("__JETONS__", jetons)
            .replace("__PIED__", pied)
            .replace("__PID__", pid)
            .replace("__NOMJS__", esc(nom_complet(p)).replace('"', "&quot;"))
            .replace("__ARBRE__", nom_arbre)
            .replace("__TITRE_ARBRE__", esc(meta.get("titre", "Arbre généalogique")))
            .replace("__NOM__", esc(nom_complet(p))))


def retirer_confidentiel(personnes):
    """Supprime physiquement les sections marquées prive du jeu de données.
    Rien n'est masqué par CSS : le contenu n'existe pas dans le fichier produit."""
    retires = 0
    for p in personnes.values():
        sections = p.get("sections")
        if not sections:
            continue
        gardees = [s for s in sections if not s.get("prive")]
        retires += len(sections) - len(gardees)
        if gardees:
            p["sections"] = gardees
        else:
            p.pop("sections", None)
    return retires


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    partage = "--partage" in sys.argv

    racine = Path(__file__).resolve().parent.parent   # le script vit dans src/
    # L'arbre du projet est celui de Samuel (décision du 2026-10-16). Le
    # fichier des Jean reste en place, mais il n'est plus la cible par
    # défaut : c'est une des quatre branches, pas l'arbre.
    source = Path(args[0]).resolve() if args else racine / "genealogie_samuel.json"

    if not source.exists():
        print(f"ERREUR : fichier introuvable -> {source}")
        return 1
    try:
        donnees = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print("ERREUR : le fichier JSON est mal formé.")
        print(f"  ligne {e.lineno}, colonne {e.colno} : {e.msg}")
        return 1

    personnes = donnees.get("personnes", {})

    # --- photos ---
    dossier_photos = source.parent / "photos"
    dossier_photos.mkdir(exist_ok=True)
    nb_photos, poids = 0, 0
    for pid, p in personnes.items():
        chemin = trouver_photo(dossier_photos, pid, p.get("photo"))
        if chemin:
            uri, taille = charger_photo(chemin)
            p["_photo"] = uri
            nb_photos += 1
            poids += taille

    # --- aide-mémoire des noms de fichiers attendus ---
    lignes = ["# Noms de fichiers attendus pour les portraits",
              "#",
              "# Déposez l'image dans ce dossier en la nommant d'après l'identifiant,",
              "# par exemple : pierre-jean-1645.jpg",
              "# Formats acceptés : " + ", ".join(e.lstrip('.') for e in EXTENSIONS),
              "# L'image est recadrée en carré et réduite automatiquement.",
              ""]
    for pid, p in sorted(personnes.items(), key=lambda kv: (kv[1].get("nom", ""), kv[1].get("prenom", ""))):
        nom = (p.get("prenom", "") + " " + p.get("nom", "")).strip()
        etat = "  [photo présente]" if p.get("_photo") else ""
        lignes.append(f"{pid + '.jpg':<34} {nom}{etat}")
    (dossier_photos / "_noms_de_fichiers.txt").write_text("\n".join(lignes) + "\n", encoding="utf-8")

    # --- confidentialité ---
    total_prive = sum(len([s for s in p.get("sections", []) if s.get("prive")])
                      for p in personnes.values())
    # Chaque section garde son rang d'origine : la version partageable en
    # retire, et une fiche qui modifie « la recette n° 3 » doit viser la
    # bonne dans le fichier de données, pas la troisième qui reste.
    for p in personnes.values():
        for i, sct in enumerate(p.get("sections") or []):
            sct["_i"] = i
    retires = retirer_confidentiel(personnes) if partage else 0

    meta = donnees.get("meta", {})
    titre = meta.get("titre", "Arbre généalogique")
    sous = meta.get("sous_titre", "")
    if partage:
        sous = (sous + " · version partageable" if sous else "version partageable")

    # chaque jeu de données a son propre dossier de fiches : pas d'écrasement
    nom_dossier_fiches = (source.stem.replace("genealogie_", "arbre_")
                          + ("_partage" if partage else "") + "_fiches")
    html = (GABARIT
            .replace("__SOURCE__", source.name)
            .replace("__DONNEES__", json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__DOSSIER_FICHES__", nom_dossier_fiches)
            .replace("__TITRE__", titre)
            .replace("__SOUS_TITRE__", sous))

    base = source.stem.replace("genealogie_", "arbre_")
    sortie = source.with_name(base + ("_partage" if partage else "") + ".html")
    if sortie == source:
        sortie = source.with_suffix(".html")
    sortie.write_text(html, encoding="utf-8")

    # --- une page complète par personne, cible du lien « En savoir plus » ---
    from datetime import date
    dossier_fiches = source.parent / nom_dossier_fiches
    dossier_fiches.mkdir(exist_ok=True)
    date_gen = date.today().strftime("%d/%m/%Y")
    attendus = set()
    # La liste des personnes, pour rattacher un fait marquant à plusieurs.
    personnes_js = json.dumps(
        sorted(([pid, nom_complet(p), vie(p)] for pid, p in personnes.items()),
               key=lambda x: x[1].lower()),
        ensure_ascii=False).replace("</", "<\\/")
    for pid in personnes:
        nom = f"{pid}.html"
        attendus.add(nom)
        legendes = {g.get("fichier"): g for g in (personnes[pid].get("galerie") or [])}
        galerie = [{"fichier": f.name, "uri": charger_image(f),
                    "legende": (legendes.get(f.name) or {}).get("legende", "")}
                   for f in photos_galerie(dossier_photos, pid)]
        (dossier_fiches / nom).write_text(
            construire_page(pid, donnees, sortie.name, date_gen, source_nom=source.name,
                            partage=partage, galerie=galerie, personnes_js=personnes_js),
            encoding="utf-8")

    # Les fiches de personnes retirées du JSON deviennent orphelines.
    # On ne supprime jamais de fichier sans le dire : on signale, c'est tout.
    orphelines = sorted(f.name for f in dossier_fiches.glob("*.html")
                        if f.name not in attendus)

    nb_p, nb_u = len(personnes), len(donnees.get("unions", []))
    nb_pb = len(donnees.get("problemes", []))
    nb_sect = sum(len(p.get("sections", [])) for p in personnes.values())
    print(f"Arbre généré : {sortie.name}  ({sortie.stat().st_size // 1024} Ko)")
    print(f"  {nb_p} personnes · {nb_u} unions · {nb_sect} sections · {nb_pb} points à vérifier")
    print(f"  {nb_p} fiches complètes dans le dossier {nom_dossier_fiches}/")
    if orphelines:
        print(f"  {len(orphelines)} fiche(s) orpheline(s) — personne retirée du JSON, "
              "fichier laissé en place :")
        for o in orphelines[:10]:
            print(f"      {o}")
        if len(orphelines) > 10:
            print(f"      … et {len(orphelines)-10} autres")
        print("      Supprimez-les vous-même si elles ne servent plus.")
    if nb_photos:
        print(f"  {nb_photos} portrait(s) integre(s) ({poids // 1024} Ko)")
    else:
        print("  aucun portrait — voir photos/_noms_de_fichiers.txt pour les noms attendus")
    if partage:
        print(f"  VERSION PARTAGEABLE : {retires} section(s) confidentielle(s) retirée(s) du fichier.")
    elif total_prive:
        print(f"  ATTENTION : {total_prive} section(s) confidentielle(s) sont DANS ce fichier.")
        print("              Pour une copie à transmettre, utilisez Generer_Version_Partageable.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
