# Annotation codebook

Each utterance gets one **function** code, one **target** code and one **stance** code: the main thing it does and the main party it is about. If a quote does two things, code the one that drives the sentence.

## Function

| Code | Definition | Example |
|---|---|---|
| ATTACK | Delegitimizes or condemns an opponent or out-group | "The Democrat Party is not a political party. It is a domestic extremist organization." |
| POWER | Asserts authority, force, state capacity, or the reach of executive power | "the president has plenary authority" |
| MOBILIZE | Rallies an in-group with emotional, sacred, or identity appeals | "You thought you could kill Charlie Kirk? You have made him immortal!" |
| POLICY | States a concrete policy goal or plan | "a goal of a minimum of 3,000 arrests for ICE every day" |
| DEFEND | Rebuts, denies, or does damage control | "To be crystal clear, I am not going anywhere." |
| LOYALTY | Praises or gives credit to the principal or the team | "I think he's a better leader now." |
| CANDOR | Gives an on-record evaluation of insiders or of the principal | "a right-wing absolute zealot" |
| MANAGE | Sets staff norms or describes process and organization | "Unauthorized leaks will not be tolerated..." |
| STRATEGY | Electoral or political strategy | "We're going to put him on the ballot." |
| PERSONAL | Personal news, gratitude | "Thank you to my family, friends, doctors..." |

## Target

OPPOSITION (Democrats, the left, protesters, NGOs) · IMMIGRANTS · COURTS · FOREIGN (other states or leaders) · MEDIA · TRUMP · INSIDERS (administration colleagues) · STAFF (subordinates, agents) · PUBLIC (voters) · SELF · NONE

## Stance (brake / accelerator)

Measures the friction a speaker adds to or removes from the principal's agenda.

| Code | Definition | Example |
|---|---|---|
| accelerator | Pushes for more executive power, force or enforcement, or for escalation against opponents | "we are looking to set a goal of a minimum of 3,000 arrests for ICE every day" |
| brake | Signals limits, disagreement, doubt or de-escalation about the principal or a policy | "There have been a couple of times where I've been outvoted." |
| neutral | Neither | "See you Monday." |

Rhetoric alone (e.g. "Change the voters, change the country") is not an accelerator unless it calls for action or power.

## Perception (L3) coding: stereotype content model

Each descriptor is scored −1 / 0 / +1 on three dimensions:

- **warmth**: friendly, trustworthy, loyal (+1) versus cold, hostile (−1)
- **competence**: effective, skilled (+1) versus ineffective, error-prone (−1)
- **dominance**: forceful, feared, commanding (+1) versus quiet, deferential (−1)

The descriptor's source is also coded: **ally** (administration or MAGA), **critic** (opponents, or intra-party critics speaking critically), or **neutral** (straight news reporting).

## v2 reliability protocol

1. Two trained human coders and one LLM coder (prompted with this codebook, temperature 0) all code a stratified 20% sample.
2. Report Krippendorff's α for each field. Revise the definitions until α ≥ 0.7.
3. The LLM codes the remainder. A human audits 10% of it, plus every case where the LLM reports low confidence.
