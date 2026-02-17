# analyze_p23_anomaly.py
"""
ANALYSE DÉTAILLÉE DE L'ANOMALIE p=23

Objectif : Identifier les 16,471 résidus mod 9699690 qui génèrent
           22 extensions au lieu de 21 lors du passage à mod 223092870.

Hypothèse : Ces résidus ont forbidden1 = forbidden2 (collision mod 23)
"""

import json
import math
from collections import Counter, defaultdict
import time


# ============================================================
# CONSTANTES
# ============================================================

MOD_PREV = 9699690
P = 23
MOD_NEW = MOD_PREV * P  # 223092870

print("="*90)
print("ANALYSE ANOMALIE p=23")
print("="*90)
print(f"\nModulus précédent : {MOD_PREV:,}")
print(f"Premier : {P}")
print(f"Modulus nouveau : {MOD_NEW:,}")
print()


# ============================================================
# CHARGEMENT DONNÉES
# ============================================================

def load_residues_9699690():
    """Charge les 378,675 résidus complets."""
    
    print("Chargement résidus mod 9699690...")
    
    try:
        with open("analysis_mod9699690_COMPLETE.json", 'r') as f:
            data = json.load(f)
        
        residues = set(data["residues_9699690_complete"])
        
        if len(residues) != 378675:
            print(f"❌ Erreur : {len(residues):,} résidus au lieu de 378,675")
            return None
        
        print(f"✓ {len(residues):,} résidus chargés")
        return residues
    
    except FileNotFoundError:
        print("❌ Fichier non trouvé : analysis_mod9699690_COMPLETE.json")
        return None


# ============================================================
# ANALYSE DES COLLISIONS
# ============================================================

def analyze_collisions(residues):
    """
    Pour chaque résidu, calcule forbidden1 et forbidden2.
    Identifie ceux où forbidden1 = forbidden2.
    """
    
    print("\n" + "="*90)
    print("ANALYSE DES COLLISIONS forbidden1 = forbidden2")
    print("="*90)
    
    collision_residues = []
    normal_residues = []
    
    # Pré-calculs
    mod_prev_mod_p = MOD_PREV % P
    two_mod_prev_mod_p = (2 * MOD_PREV) % P
    
    if mod_prev_mod_p == 0 or two_mod_prev_mod_p == 0:
        print(f"⚠️ Cas spécial détecté")
        print(f"  mod_prev mod {P} = {mod_prev_mod_p}")
        print(f"  2×mod_prev mod {P} = {two_mod_prev_mod_p}")
    
    inv_mod = pow(mod_prev_mod_p, -1, P) if mod_prev_mod_p != 0 else None
    inv_2mod = pow(two_mod_prev_mod_p, -1, P) if two_mod_prev_mod_p != 0 else None
    
    print(f"\nPré-calculs :")
    print(f"  {MOD_PREV:,} mod {P} = {mod_prev_mod_p}")
    print(f"  2×{MOD_PREV:,} mod {P} = {two_mod_prev_mod_p}")
    print(f"  Inverse de {mod_prev_mod_p} mod {P} = {inv_mod}")
    print(f"  Inverse de {two_mod_prev_mod_p} mod {P} = {inv_2mod}")
    
    print(f"\nAnalyse des {len(residues):,} résidus...")
    
    count = 0
    start_time = time.time()
    
    for r in residues:
        count += 1
        
        if count % 50000 == 0:
            elapsed = time.time() - start_time
            rate = count / elapsed if elapsed > 0 else 0
            eta = (len(residues) - count) / rate if rate > 0 else 0
            print(f"  {count:,}/{len(residues):,} ({100*count/len(residues):.1f}%) | ETA: {eta:.0f}s")
        
        # Calculer forbidden1
        if mod_prev_mod_p == 0:
            if r % P == 0:
                continue  # Skip
            forbidden1 = None
        else:
            forbidden1 = ((-r % P) * inv_mod) % P
        
        # Calculer forbidden2
        if two_mod_prev_mod_p == 0:
            if (2*r + 1) % P == 0:
                continue  # Skip
            forbidden2 = None
        else:
            forbidden2 = ((-(2*r + 1) % P) * inv_2mod) % P
        
        # Vérifier collision
        if forbidden1 is not None and forbidden2 is not None:
            if forbidden1 == forbidden2:
                collision_residues.append(r)
            else:
                normal_residues.append(r)
    
    print(f"\n✓ Analyse terminée")
    
    return collision_residues, normal_residues


# ============================================================
# ANALYSE STATISTIQUE
# ============================================================

def analyze_statistics(collision_residues, normal_residues):
    """Analyse statistique des résidus."""
    
    print("\n" + "="*90)
    print("STATISTIQUES")
    print("="*90)
    
    total = len(collision_residues) + len(normal_residues)
    
    print(f"\nTotal résidus analysés : {total:,}")
    print(f"Résidus avec collision : {len(collision_residues):,} ({100*len(collision_residues)/total:.3f}%)")
    print(f"Résidus normaux        : {len(normal_residues):,} ({100*len(normal_residues)/total:.3f}%)")
    
    # Attendu vs observé
    print(f"\n" + "-"*90)
    print("COMPARAISON AVEC ANOMALIE OBSERVÉE")
    print("-"*90)
    
    expected_anomaly = 16471
    observed_collision = len(collision_residues)
    
    print(f"\nRésidus anormaux observés (22 ext) : {expected_anomaly:,}")
    print(f"Résidus avec collision calculés    : {observed_collision:,}")
    print(f"Différence                         : {observed_collision - expected_anomaly:,}")
    
    if observed_collision == expected_anomaly:
        print("\n✓✓✓ PARFAIT : Les collisions expliquent EXACTEMENT l'anomalie !")
    elif abs(observed_collision - expected_anomaly) < 100:
        print("\n✓✓ Excellent : Les collisions expliquent l'anomalie (~100 près)")
    else:
        print(f"\n⚠️ Écart significatif : {abs(observed_collision - expected_anomaly):,}")
    
    return {
        "total": total,
        "collisions": len(collision_residues),
        "normal": len(normal_residues),
        "expected_anomaly": expected_anomaly
    }


# ============================================================
# ANALYSE MOD 23
# ============================================================

def analyze_mod23_distribution(collision_residues, normal_residues):
    """Analyse la distribution mod 23."""
    
    print("\n" + "="*90)
    print("DISTRIBUTION MOD 23")
    print("="*90)
    
    # Distribution résidus avec collision
    collision_mod23 = Counter(r % P for r in collision_residues)
    
    print(f"\nRésidus avec collision mod {P} :")
    for val in sorted(collision_mod23.keys()):
        count = collision_mod23[val]
        pct = 100 * count / len(collision_residues) if collision_residues else 0
        print(f"  r ≡ {val:2d} (mod {P}) : {count:,} résidus ({pct:.2f}%)")
    
    # Distribution résidus normaux
    normal_mod23 = Counter(r % P for r in normal_residues[:10000])  # Échantillon
    
    print(f"\nRésidus normaux mod {P} (échantillon 10k) :")
    for val in sorted(normal_mod23.keys())[:10]:
        count = normal_mod23[val]
        pct = 100 * count / 10000
        print(f"  r ≡ {val:2d} (mod {P}) : {count:,} résidus ({pct:.2f}%)")


# ============================================================
# ANALYSE MOD 30
# ============================================================

def analyze_mod30_distribution(collision_residues):
    """Analyse la distribution mod 30."""
    
    print("\n" + "="*90)
    print("DISTRIBUTION MOD 30 DES RÉSIDUS AVEC COLLISION")
    print("="*90)
    
    collision_mod30 = Counter(r % 30 for r in collision_residues)
    
    print(f"\nRésidus avec collision mod 30 :")
    for val in sorted(collision_mod30.keys()):
        count = collision_mod30[val]
        pct = 100 * count / len(collision_residues) if collision_residues else 0
        print(f"  r ≡ {val:2d} (mod 30) : {count:,} résidus ({pct:.2f}%)")
    
    # Vérifier symétrie
    counts_30 = [collision_mod30[11], collision_mod30[23], collision_mod30[29]]
    
    if len(set(counts_30)) == 1:
        print(f"\n✓ Symétrie parfaite mod 30")
    else:
        avg = sum(counts_30) / 3
        max_dev = max(abs(c - avg) for c in counts_30)
        print(f"\n⚠️ Asymétrie mod 30 : écart max {max_dev:,.0f}")


# ============================================================
# VÉRIFICATION THÉORIQUE
# ============================================================

def verify_collision_condition(collision_residues):
    """
    Vérifie la condition mathématique pour forbidden1 = forbidden2.
    
    forbidden1 = (-r) / mod_prev (mod 23)
    forbidden2 = -(2r+1) / (2×mod_prev) (mod 23)
    
    forbidden1 = forbidden2  ⟺
    (-r) / mod_prev ≡ -(2r+1) / (2×mod_prev) (mod 23)
    -r × 2 ≡ -(2r+1) (mod 23)
    -2r ≡ -2r - 1 (mod 23)
    0 ≡ -1 (mod 23)
    
    IMPOSSIBLE ! Donc il doit y avoir autre chose...
    """
    
    print("\n" + "="*90)
    print("VÉRIFICATION CONDITION THÉORIQUE")
    print("="*90)
    
    print("\nCondition pour collision forbidden1 = forbidden2 :")
    print("  (-r) / mod_prev ≡ -(2r+1) / (2×mod_prev) (mod 23)")
    print("  Simplifie à : 0 ≡ -1 (mod 23)")
    print("  → IMPOSSIBLE !")
    
    print("\n⚠️ La collision ne peut PAS venir de l'égalité algébrique")
    print("   Il doit y avoir un autre mécanisme...")
    
    # Vérifier échantillon
    if collision_residues:
        print(f"\nVérification sur échantillon de 10 résidus avec collision :")
        
        mod_prev_mod_p = MOD_PREV % P
        two_mod_prev_mod_p = (2 * MOD_PREV) % P
        inv_mod = pow(mod_prev_mod_p, -1, P)
        inv_2mod = pow(two_mod_prev_mod_p, -1, P)
        
        for r in list(collision_residues)[:10]:
            forbidden1 = ((-r % P) * inv_mod) % P
            forbidden2 = ((-(2*r + 1) % P) * inv_2mod) % P
            
            print(f"  r={r:8d} : forbidden1={forbidden1:2d}, forbidden2={forbidden2:2d}, égal={forbidden1==forbidden2}")


# ============================================================
# SAUVEGARDE
# ============================================================

def save_results(collision_residues, stats):
    """Sauvegarde les résultats."""
    
    data = {
        "prime": P,
        "modulus_prev": MOD_PREV,
        "total_residues": stats["total"],
        "collision_residues_count": len(collision_residues),
        "normal_residues_count": stats["normal"],
        "expected_anomaly": stats["expected_anomaly"],
        "collision_residues_sample": sorted(collision_residues)[:1000]
    }
    
    filename = "p23_anomaly_analysis.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Résultats sauvegardés : {filename}")


# ============================================================
# MAIN
# ============================================================

def main():
    """Script principal."""
    
    # Chargement
    residues = load_residues_9699690()
    
    if residues is None:
        print("\n❌ ÉCHEC")
        return
    
    # Analyse collisions
    collision_residues, normal_residues = analyze_collisions(residues)
    
    # Statistiques
    stats = analyze_statistics(collision_residues, normal_residues)
    
    # Distribution mod 23
    analyze_mod23_distribution(collision_residues, normal_residues)
    
    # Distribution mod 30
    analyze_mod30_distribution(collision_residues)
    
    # Vérification théorique
    verify_collision_condition(collision_residues)
    
    # Sauvegarde
    print("\n" + "="*90)
    print("SAUVEGARDE")
    print("="*90)
    
    save_results(collision_residues, stats)
    
    # Résumé
    print("\n" + "="*90)
    print("CONCLUSION")
    print("="*90)
    
    if len(collision_residues) == stats["expected_anomaly"]:
        print("\n✓✓✓ HYPOTHÈSE CONFIRMÉE :")
        print(f"    Les {len(collision_residues):,} résidus avec forbidden1=forbidden2")
        print(f"    correspondent EXACTEMENT aux {stats['expected_anomaly']:,} résidus anormaux")
    else:
        print(f"\n⚠️ HYPOTHÈSE À RÉVISER :")
        print(f"    Collisions calculées : {len(collision_residues):,}")
        print(f"    Anomalie observée    : {stats['expected_anomaly']:,}")
        print(f"    Il y a un autre mécanisme en jeu...")


if __name__ == "__main__":
    main()
