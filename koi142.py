"""KOI 142 test for Ben Montet."""
from ttv_devil import Body, System, SECOND, MINUTE, HOUR
import matplotlib.pyplot as pl


def KingOfTTVs(days=2000):
    """Plot the TTV curves for KOI 142 b and c."""
    # Star (at origin)
    star = Body('star', 0.956, 0, 0, 0, 0, 0, 0)

    # Planet b
    b = Body('b', 0.00003398527, 2.468048754640008e-02, 1.430942213992328e-03,
             9.273805877239813e-02, -5.284347573571933e-02,
             1.696196988487972e-04, 1.099289785917278e-02)

    # Planet c
    c = Body('c', 0.00061365001, 1.290927890560793e-01, -6.260295033163559e-03,
             -6.524922742997734e-02, 1.952208933275210e-02,
             2.894719946941922e-03, 4.081951683817600e-02)

    # Integration start (days)
    t0 = 54.627020

    # REBOUND timestep
    dt_reb = 1 * MINUTE

    # Search for transits every...
    dt_trn = 12 * HOUR

    # Transit time tolerance
    tol = 1 * SECOND

    # Compute
    system = System(star, b, c, dt_reb=dt_reb, dt_trn=dt_trn, tol=tol)
    system.compute(t0, t0 + days)

    # NOTE: The ttvs are stored in b.ttvs
    # but the actual transit times are stored in b.transit_times

    # Plot
    fig, ax = pl.subplots(2, figsize=(7, 8))
    ax[0].plot(range(b.nt), b.ttvs / HOUR, '.', ms=3, color='C0')
    ax[0].plot(range(b.nt), b.ttvs / HOUR, '-', color='C0', lw=1, alpha=0.3)
    ax[1].plot(range(c.nt), c.ttvs / HOUR, '.', ms=3, color='C1')
    ax[1].plot(range(c.nt), c.ttvs / HOUR, '-', color='C1', lw=1, alpha=0.3)
    ax[0].set_ylabel('b TTVs [hours]', fontweight='bold')
    ax[1].set_ylabel('c TTVs [hours]', fontweight='bold')
    ax[0].set_xlabel('Transit number', fontweight='bold')
    ax[1].set_xlabel('Transit number', fontweight='bold')
    pl.show()


if __name__ == "__main__":
    KingOfTTVs()
