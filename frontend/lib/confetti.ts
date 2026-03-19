import confetti from 'canvas-confetti'

/**
 * Fire a celebration confetti effect
 * Uses falling confetti from top with layered bursts for realistic look
 * Respects user's reduced motion preference
 */
export function fireConfetti() {
  const count = 200
  const defaults: confetti.Options = {
    origin: { y: 0.7 },
    zIndex: 9999,
    disableForReducedMotion: true,
  }

  function fire(particleRatio: number, opts: confetti.Options) {
    confetti({
      ...defaults,
      ...opts,
      particleCount: Math.floor(count * particleRatio),
    })
  }

  fire(0.25, { spread: 26, startVelocity: 55 })
  fire(0.2, { spread: 60 })
  fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8 })
  fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2 })
  fire(0.1, { spread: 120, startVelocity: 45 })
}
