#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 13:33:55 2022.

@author: fabian
"""

from functools import cached_property

import numpy as np
import pandas as pd


def create_vector(indices, values, fill_value=np.nan):
    """Create a vector of a size equal to the maximum index plus one."""
    vector = np.full(max(indices) + 1, fill_value)
    vector[indices] = values
    return vector


class MatrixAccessor:
    """
    Helper class to quickly access model related vectors and matrices.
    """

    def __init__(self, model):
        self._parent = model

    @cached_property
    def flat_vars(self):
        m = self._parent
        return m.variables.flat

    @cached_property
    def flat_cons(self):
        m = self._parent
        return m.constraints.flat

    @property
    def vlabels(self):
        "Vector of labels of all non-missing variables."
        df = self.flat_vars
        return create_vector(df.key, df.labels, -1)

    @property
    def vtypes(self):
        "Vector of types of all non-missing variables."
        m = self._parent
        df = self.flat_vars
        specs = []
        for name in m.variables:
            if name in m.binaries:
                val = "B"
            elif name in m.integers:
                val = "I"
            else:
                val = "C"
            specs.append(pd.Series(val, index=m.variables[name].flat.labels))

        ds = pd.concat(specs)
        ds = df.set_index("key").labels.map(ds)
        return create_vector(ds.index, ds.values, "")

    @property
    def lb(self):
        "Vector of lower bounds of all non-missing variables."
        df = self.flat_vars
        return create_vector(df.key, df.lower)

    @property
    def ub(self):
        "Vector of upper bounds of all non-missing variables."
        df = self.flat_vars
        return create_vector(df.key, df.upper)

    @property
    def clabels(self):
        "Vector of labels of all non-missing constraints."
        df = self.flat_cons
        return create_vector(df.key, df.labels, -1)

    @property
    def A(self):
        "Constraint matrix of all non-missing constraints and variables."
        m = self._parent
        return m.constraints.to_matrix(filter_missings=False)[self.clabels][
            :, self.vlabels
        ]

    @property
    def sense(self):
        "Vector of senses of all non-missing constraints."
        df = self.flat_cons
        return create_vector(df.key, df.sign.astype(np.dtype("<U1")), "")

    @property
    def b(self):
        "Vector of right-hand-sides of all non-missing constraints."
        df = self.flat_cons
        return create_vector(df.key, df.rhs)

    @property
    def c(self):
        "Vector of objective coefficients of all non-missing variables."
        m = self._parent
        ds = m.objective.flat
        vars = ds.vars.map(self.flat_vars.set_index("labels").key)
        return create_vector(vars, ds.coeffs, 0)
