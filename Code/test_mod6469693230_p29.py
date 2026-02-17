# test_mod6469693230_p29.py
"""
TEST p=29 : Calcul de ε(29)
Modulus : 6,469,693,230 = 223,092,870 × 29
Prédiction : 7,968,646 × 27 = 215,153,442 résidus

Objectif : Déterminer si l'anomalie persiste et calculer ε(29)
"""

import math
import json
from datetime import datetime
from collections import defaultdict, Counter
import time


# ============================================================
# CONSTANTES
# ============================================================

MOD_PREV = 223092870
P_NEW = 29
MOD_NEW = MOD_PREV * P_NEW  # 6,469,693,230

print("="*90)
print("TEST p=29 : CALCUL DE ε(29)")
print("="*90)
print(f"\nModulus : {MOD_NEW:,} = {MOD_PREV:,} × {P_NEW}")
print(f"Prédiction : 7,968,646 × 27 = 215,153,442 résidus")
print(f"Facteur théorique : {P_NEW - 2}")
print()


# ============================================================
# CHARGEMENT DONNÉES MOD 223092870
# ============================================================

def load_residues_223092870():
    """
    Charge les résidus depuis le recalcul précédent.
    
    PROBLÈME : Le fichier JSON ne contient qu'un échantillon !
    Solution : Régénérer à partir de mod 9699690.
    """
    
    print("Chargement des résidus mod 223092870...")
    
    # Tentative 1 : Charger depuis JSON recalculé
    try:
        with open("analysis_mod223092870_RECALCULATED.json", 'r') as f:
            data = json.load(f)
        
        # Vérifier si résidus complets disponibles
        if "residues_223092870_complete" in data:
            residues = set(data["residues_223092870_complete"])
            print(f"✓ {len(residues):,} résidus chargés depuis JSON")
            return residues
        else:
            print(f"⚠ JSON contient seulement statistiques, régénération nécessaire")
    
    except FileNotFoundError:
        print(f"⚠ Fichier non trouvé, régénération nécessaire")
    
    # Régénération depuis mod 9699690
    print("\nRégénération mod 223092870 depuis mod 9699690...")
    
    residues_9699690 = load_residues_9699690()
    
    if residues_9699690 is None:
        return None
    
    residues_223092870 = generate_via_crt(residues_9699690, 9699690, 23, 223092870)
    
    print(f"✓ {len(residues_223092870):,} résidus mod 223092870 générés")
    
    return residues_223092870


def load_residues_9699690():
    """Charge les 378,675 résidus complets mod 9699690."""
    
    print("  Chargement mod 9699690...")
    
    try:
        with open("analysis_mod9699690_COMPLETE.json", 'r') as f:
            data = json.load(f)
        
        residues = set(data["residues_9699690_complete"])
        
        if len(residues) != 378675:
            print(f"  ✗ Erreur : {len(residues):,} résidus au lieu de 378,675")
            return None
        
        print(f"  ✓ {len(residues):,} résidus mod 9699690 chargés")
        return residues
    
    except FileNotFoundError:
        print(f"  ✗ Fichier non trouvé : analysis_mod9699690_COMPLETE.json")
        return None


# ============================================================
# GÉNÉRATION VIA CRT
# ============================================================

def generate_via_crt(residues_prev, mod_prev, p_new, mod_new):
    """
    Génération hiérarchique par CRT.
    Version optimisée avec compteurs de progression.
    """
    
    print(f"\n  Génération mod {mod_new:,} via CRT...")
    print(f"  → {len(residues_prev):,} résidus × {p_new-2} extensions attendues")
    print()
    
    residues_new = set()
    
    count = 0
    total = len(residues_prev)
    start_time = time.time()
    
    for r_prev in residues_prev:
        count += 1
        
        # Progression
        if count % 50000 == 0:
            elapsed = time.time() - start_time
            rate = count / elapsed if elapsed > 0 else 0
            eta = (total - count) / rate if rate > 0 else 0
            
            print(f"  {count:,}/{total:,} ({100*count/total:.1f}%) | "
                  f"{rate:,.0f} res/s | ETA: {eta:.0f}s")
        
        # Valeurs interdites
        mod_prev_mod_p = mod_prev % p_new
        
        # forbidden1
        if mod_prev_mod_p == 0:
            if r_prev % p_new == 0:
                continue
            forbidden1 = None
        else:
            inv_mod = pow(mod_prev_mod_p, -1, p_new)
            forbidden1 = ((-r_prev % p_new) * inv_mod) % p_new
        
        # forbidden2
        two_mod_prev_mod_p = (2 * mod_prev) % p_new
        
        if two_mod_prev_mod_p == 0:
            if (2*r_prev + 1) % p_new == 0:
                continue
            forbidden2 = None
        else:
            inv_2mod = pow(two_mod_prev_mod_p, -1, p_new)
            forbidden2 = ((-(2*r_prev + 1) % p_new) * inv_2mod) % p_new
        
        # Générer extensions
        for t in range(p_new):
            if t == forbidden1 or t == forbidden2:
                continue
            
            x = r_prev + mod_prev * t
            residues_new.add(x)
    
    elapsed = time.time() - start_time
    print(f"\n  ✓ Génération terminée")
    print(f"    Temps : {elapsed:.1f}s")
    print(f"    Vitesse : {len(residues_new)/elapsed:,.0f} résidus/s")
    
    return residues_new


# ============================================================
# ANALYSE STATISTIQUE
# ============================================================

def analyze_distribution(residues_new, residues_prev):
    """Analyse la distribution des extensions."""
    
    print("\n" + "="*90)
    print("ANALYSE STATISTIQUE")
    print("="*90)
    
    observed = len(residues_new)
    predicted = len(residues_prev) * (P_NEW - 2)
    
    print(f"\nRésidus mod {MOD_PREV:,}  : {len(residues_prev):,}")
    print(f"Résidus mod {MOD_NEW:,} : {observed:,}")
    print(f"Prédiction                  : {predicted:,}")
    print(f"Écart                       : {observed - predicted:+,} ({100*(observed - predicted)/predicted:+.4f}%)")
    print()
    print(f"Ratio observé               : {observed / len(residues_prev):.6f}")
    print(f"Ratio théorique             : {P_NEW - 2:.6f}")
    print(f"ε({P_NEW})                       : {observed / len(residues_prev) - (P_NEW - 2):+.6f}")
    
    # Conclusion rapide
    print()
    if observed == predicted:
        print("✓✓✓ PARFAIT : Ratio exact !")
    elif abs(observed - predicted) / predicted < 0.001:
        print("✓✓ Excellent : Écart < 0.1%")
    elif abs(observed - predicted) / predicted < 0.01:
        print("✓ Bon : Écart < 1%")
    else:
        print(f"⚠ Écart significatif : {100*abs(observed - predicted)/predicted:.2f}%")
    
    return {
        "observed": observed,
        "predicted": predicted,
        "ratio": observed / len(residues_prev),
        "epsilon": observed / len(residues_prev) - (P_NEW - 2),
        "error_pct": 100 * (observed - predicted) / predicted
    }


def analyze_uniformity(residues_new, residues_prev):
    """Analyse l'uniformité des extensions (échantillonnage)."""
    
    print("\n" + "="*90)
    print("ANALYSE UNIFORMITÉ (ÉCHANTILLON)")
    print("="*90)
    
    print("\nCalcul du nombre d'extensions par résidu...")
    print("(Échantillonnage sur premiers 100,000 résidus pour rapidité)")
    
    # Échantillonner pour rapidité
    sample_size = min(100000, len(residues_new))
    residues_sample = list(residues_new)[:sample_size]
    
    groups = defaultdict(list)
    
    for r in residues_sample:
        r_prev = r % MOD_PREV
        groups[r_prev].append(r)
    
    extension_counts = [len(groups[r]) for r in groups.keys()]
    
    if not extension_counts:
        print("⚠ Aucune donnée pour analyse uniformité")
        return {}
    
    print(f"\nStatistiques (sur échantillon de {len(groups):,} résidus) :")
    print(f"  Min     : {min(extension_counts)}")
    print(f"  Max     : {max(extension_counts)}")
    print(f"  Moyenne : {sum(extension_counts)/len(extension_counts):.6f}")
    
    # Distribution
    count_dist = Counter(extension_counts)
    
    print(f"\nDistribution :")
    for count in sorted(count_dist.keys()):
        freq = count_dist[count]
        pct = 100 * freq / len(groups)
        print(f"  {count:2d} extensions : {freq:,} résidus ({pct:.3f}%)")
    
    # Uniformité
    if len(set(extension_counts)) == 1:
        print(f"\n✓✓✓ UNIFORMITÉ PARFAITE : {extension_counts[0]} extensions chacun")
        uniform = True
    else:
        std_dev = (sum((x - (P_NEW-2))**2 for x in extension_counts) / len(extension_counts))**0.5
        print(f"\n⚠ VARIATIONS DÉTECTÉES")
        print(f"  Écart-type : {std_dev:.4f}")
        print(f"  Variation  : {100*std_dev/(P_NEW-2):.3f}%")
        uniform = False
    
    return {
        "uniform": uniform,
        "min": min(extension_counts),
        "max": max(extension_counts),
        "mean": sum(extension_counts) / len(extension_counts),
        "distribution": dict(count_dist)
    }


# ============================================================
# COMPARAISON AVEC p=23
# ============================================================

def compare_with_p23():
    """Compare les résultats avec p=23."""
    
    print("\n" + "="*90)
    print("COMPARAISON p=23 vs p=29")
    print("="*90)
    
    # Données p=23
    epsilon_23 = 0.0435
    non_uniform_23 = 4.35  # Pourcentage
    
    print(f"\np=23 :")
    print(f"  ε(23)           : +{epsilon_23:.4f}")
    print(f"  Non-uniformité  : {non_uniform_23:.2f}%")
    print(f"  Ratio           : 21.0435")
    
    print(f"\np=29 :")
    print(f"  ε(29)           : [À CALCULER]")
    print(f"  Non-uniformité  : [À CALCULER]")
    print(f"  Ratio           : [À CALCULER]")


# ============================================================
# SAUVEGARDE
# ============================================================

def save_results(stats_dist, stats_unif):
    """Sauvegarde les résultats."""
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "modulus": MOD_NEW,
        "modulus_previous": MOD_PREV,
        "prime_factor": P_NEW,
        "summary": {
            "residues_prev": 7968646,  # Approximatif si non exact
            "residues_observed": stats_dist["observed"],
            "residues_predicted": stats_dist["predicted"],
            "ratio": stats_dist["ratio"],
            "epsilon": stats_dist["epsilon"],
            "theoretical_factor": P_NEW - 2
        },
        "statistics": {
            "distribution": stats_dist,
            "uniformity": stats_unif
        }
    }
    
    filename = "analysis_mod6469693230_p29.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Résultats sauvegardés : {filename}")


# ============================================================
# MAIN
# ============================================================

def main():
    """Script principal."""
    
    start_total = time.time()
    
    # Chargement
    print("="*90)
    print("ÉTAPE 1 : CHARGEMENT DONNÉES MOD 223092870")
    print("="*90)
    print()
    
    residues_prev = load_residues_223092870()
    
    if residues_prev is None:
        print("\n✗ ÉCHEC : Impossible de charger/générer les données")
        return
    
    print(f"\n✓ {len(residues_prev):,} résidus mod 223092870 prêts")
    
    # Génération
    print("\n" + "="*90)
    print("ÉTAPE 2 : GÉNÉRATION MOD 6469693230 (p=29)")
    print("="*90)
    
    residues_new = generate_via_crt(residues_prev, MOD_PREV, P_NEW, MOD_NEW)
    
    print(f"\n✓ {len(residues_new):,} résidus générés")
    
    # Analyse distribution
    stats_dist = analyze_distribution(residues_new, residues_prev)
    
    # Analyse uniformité (échantillon)
    stats_unif = analyze_uniformity(residues_new, residues_prev)
    
    # Comparaison
    compare_with_p23()
    
    # Sauvegarde
    print("\n" + "="*90)
    print("SAUVEGARDE")
    print("="*90)
    
    save_results(stats_dist, stats_unif)
    
    # Résumé final
    elapsed_total = time.time() - start_total
    
    print("\n" + "="*90)
    print("RÉSUMÉ FINAL")
    print("="*90)
    
    print(f"\nRésidus générés  : {stats_dist['observed']:,}")
    print(f"Ratio observé    : {stats_dist['ratio']:.6f}")
    print(f"ε({P_NEW})            : {stats_dist['epsilon']:+.6f}")
    print(f"Écart            : {stats_dist['error_pct']:.4f}%")
    
    if stats_unif.get("uniform"):
        print(f"Uniformité       : ✓ PARFAITE")
    elif "mean" in stats_unif:
        print(f"Uniformité       : ⚠ Variations")
    
    print(f"\nTemps total      : {elapsed_total:.1f}s")
    
    # Conclusion
    print("\n" + "="*90)
    print("CONCLUSION")
    print("="*90)
    print()
    
    if abs(stats_dist['epsilon']) < 0.001:
        print("✓✓✓ PAS D'ANOMALIE : ε(29) ≈ 0")
        print("    → L'anomalie p=23 était isolée")
    elif 0.001 <= abs(stats_dist['epsilon']) < 0.05:
        print("✓✓ LÉGÈRE ANOMALIE : ε(29) ≈ " + f"{stats_dist['epsilon']:.4f}")
        print("    → Pattern similaire à p=23")
    else:
        print("⚠ FORTE ANOMALIE : ε(29) = " + f"{stats_dist['epsilon']:.4f}")
        print("    → Écart significatif de la loi p-2")
    
    # Tendance
    if abs(stats_dist['epsilon']) > 0.001:
        epsilon_23 = 0.0435
        epsilon_29 = stats_dist['epsilon']
        
        print(f"\nTendance :")
        print(f"  ε(23) = {epsilon_23:+.4f}")
        print(f"  ε(29) = {epsilon_29:+.4f}")
        
        if abs(epsilon_29) > abs(epsilon_23):
            print(f"  → Amplification : ×{abs(epsilon_29/epsilon_23):.2f}")
        elif abs(epsilon_29) < abs(epsilon_23):
            print(f"  → Atténuation : ×{abs(epsilon_29/epsilon_23):.2f}")
        else:
            print(f"  → Stabilité")
    
    print("\n" + "="*90)


if __name__ == "__main__":
    main()
