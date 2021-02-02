from functools import partial

from invoke import task, run


sh = partial(run, echo=True)


@task
def lint(c):
    sh("pylint configsuite_tui")


@task
def check(c):
    sh("black --check --verbose --diff .")
    sh("flake8")


@task
def test(c):
    sh("coverage run --source='.' -m unittest discover", pty=True)
    sh("coverage xml -o cobertura.xml")
