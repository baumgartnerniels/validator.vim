# -*- coding: utf-8 -*-

from __future__ import print_function

import collections
import vim
import uuid

from fixup.utils import g


class SignNotifier(object):
    sign_ids = collections.defaultdict(list)

    def refresh(self, bugs, bufnr):
        if bufnr < 0:
            return

        self.bufnr = bufnr

        self._remove_signs()
        self._sign_error(bugs)

    def _sign_error(self, bugs):
        if not bugs:
            return

        seen = {}

        for i in bugs:
            if i['lnum'] > 0 and i["lnum"] not in seen:
                seen[i["lnum"]] = True

                sign_severity = "Warning" if i["type"] == 'W' else "Error"
                sign_subtype = i.get("subtype", '')
                sign_type = "Fixup{}{}".format(sign_subtype, sign_severity)

                sign_id = int(uuid.uuid4().int >> 100)

                p_fmt = ('try | '
                         'exec "sign place {} line={} name={} buffer={}" | '
                         'catch /E158/ | '
                         'endtry')
                vim.command(p_fmt.format(
                    sign_id, i["lnum"], sign_type, i["bufnr"]))

                self.sign_ids[self.bufnr].append(sign_id)

    def _remove_signs(self):
        if not hasattr(self, "bufnr"):
            return

        for i in reversed(self.sign_ids.get(self.bufnr, [])):
            unplace_fmt = ('try | '
                           'exec "sign unplace {} buffer={}" | '
                           'catch /E158/ | '
                           'endtry')
            vim.command(unplace_fmt.format(i, self.bufnr))
            self.sign_ids[self.bufnr].remove(i)


class CursorNotifier(object):
    def refresh(self):
        g["refresh_cursor"] = True
