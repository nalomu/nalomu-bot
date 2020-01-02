from nalomu.commands import BaseCommand, method_command, method_parser, method_nlp
from random import Random


class RollCommands(BaseCommand):

    @method_command('roll', aliases=('摇', '摇号'), only_to_me=False)
    async def get_roll(self):
        num1 = self.get('num1')
        num2 = self.get('num2')

        await self.send(str(self.roll(max(num1, num2), min(num1, num2))))

    @get_roll.args_parser
    @method_parser
    async def _(self):
        text = self.stripped_msg

        if self.session.is_first_run:
            if text:
                print(text)
                args = text.split(' ')
                print(args)
                self.session.state['num1'] = int(args[0]) if len(args) >= 1 else 100
                self.session.state['num2'] = int(args[1]) if len(args) >= 2 else 0
            else:
                self.session.state['num1'] = 100
                self.session.state['num2'] = 0
            return

        self.session.state[self.session.current_key] = text

    @staticmethod
    def roll(max_num=100, min_num=0):
        return Random().randint(min_num, max_num)


__all__ = ['RollCommands']
