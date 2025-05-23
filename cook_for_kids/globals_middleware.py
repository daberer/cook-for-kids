import pandas as pd

class SetupSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # At the beginning of each request, load from session into globals
        from globals import Setup  # Import your Setup class

        # Initialize session if needed
        if 'setup_df' not in request.session:
            request.session['setup_df'] = pd.DataFrame().to_dict()
        if 'setup_optimise' not in request.session:
            request.session['setup_optimise'] = False
        if 'setup_trial_number' not in request.session:
            request.session['setup_trial_number'] = 1000
        if 'setup_excursion_day' not in request.session:
            request.session['setup_excursion_day'] = (True, 1)

        # Load from session to globals
        Setup.df = pd.DataFrame(request.session['setup_df'])
        Setup.optimise = request.session['setup_optimise']
        Setup.trial_number = request.session['setup_trial_number']
        Setup.excursion_day = request.session['setup_excursion_day']

        # Process the request
        response = self.get_response(request)

        # After the request, save globals back to session
        request.session['setup_df'] = Setup.df.to_dict() if Setup.df is not None else {}
        request.session['setup_optimise'] = Setup.optimise
        request.session['setup_trial_number'] = Setup.trial_number
        request.session['setup_excursion_day'] = Setup.excursion_day

        return response
