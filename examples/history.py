#  Copyright (c) 2020. Davi Pereira dos Santos
#      This file is part of the aiuna project.
#      Please respect the license. Removing authorship by any means
#      (by code make up or closing the sources) or ignoring property rights
#      is a crime and is unethical regarding the effort and time spent here.
#      Relevant employers or funding agencies will be notified accordingly.
#
#      aiuna is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      aiuna is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with aiuna.  If not, see <http://www.gnu.org/licenses/>.
#

# Checking history
import aiuna.pack

X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d.history)
# ...

del d["X"]
print(d.history)
# ...

d["Z"] = 42
print(d.Z, type(d.Z))
# ...

print(d.history)
# ...
