# Part of OCA. See LICENSE file for full copyright and licensing details.

from . import models
from . import wizard


def post_migrate_hook(env):
    """
    Runs on install AND upgrade.
    1. Creates the Salary Journal if missing
    2. Sets it as default on all contracts missing a journal
    3. Maps SCF accounts to all Algerian salary rules
    """
    _ensure_paie_journal(env)
    _map_salary_rule_accounts(env)


def _ensure_paie_journal(env):
    Journal = env["account.journal"]
    company = env.company

    journal = Journal.search([
        ("code", "=", "PAIE"),
        ("company_id", "=", company.id),
    ], limit=1)

    if not journal:
        journal = Journal.create({
            "name": "Journal de Paie",
            "code": "PAIE",
            "type": "general",
            "company_id": company.id,
        })

    # Set journal on all contracts that don't have one
    contracts = env["hr.contract"].search([
        ("journal_id", "=", False),
        ("company_id", "=", company.id),
    ])
    if contracts:
        contracts.write({"journal_id": journal.id})


def _map_salary_rule_accounts(env):
    """Map SCF accounts to Algerian salary rules."""
    Account = env["account.account"]
    Rule = env["hr.salary.rule"]

    def get_acc(code):
        return Account.search([("code", "=", code)], limit=1)

    acc_631 = get_acc("631000")  # Remunerations du personnel
    acc_421 = get_acc("421000")  # Personnel, salaires dus
    acc_431 = get_acc("431000")  # Securite sociale / CNAS
    acc_447 = get_acc("447800")  # Autres impots IRG
    acc_512 = get_acc("512001")  # Banque

    mappings = [
        # (rule_code, debit_account, credit_account)
        ("SB",        acc_631, acc_421),
        ("SP",        acc_631, acc_421),
        ("IEP",       acc_631, acc_421),
        ("PANIER",    acc_631, acc_421),
        ("TRANSPORT", acc_631, acc_421),
        ("PRI_RDT",   acc_631, acc_421),
        ("AF",        acc_631, acc_421),
        ("SU",        acc_631, acc_421),
        ("BRUT",      acc_631, acc_421),
        ("CNAS_SAL",  acc_421, acc_431),
        ("IRG",       acc_421, acc_447),
        ("NET",       acc_421, acc_512),
        ("CNAS_PAT",  acc_631, acc_431),
    ]

    for code, debit, credit in mappings:
        rule = Rule.search([("code", "=", code)], limit=1)
        if rule and debit and credit:
            rule.write({
                "account_debit": debit.id,
                "account_credit": credit.id,
            })
