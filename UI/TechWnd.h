// -*- C++ -*-
#ifndef _TechWnd_h_
#define _TechWnd_h_

#include "CUI_Wnd.h"

class CUIScroll;
class Tech;
namespace GG {class RadioButtonGroup;}

class TechTreeWnd : public GG::Wnd
{
public:
    enum TechTypesShown {
        THEORY_TECHS,
        APPLICATION_AND_THEORY_TECHS,
        ALL_TECHS
    };

    /** \name Signal Types */ //@{
    typedef boost::signal<void (const Tech*)>      TechBrowsedSignalType;       ///< emitted when a technology is single-clicked
    typedef boost::signal<void (const Tech*)>      TechClickedSignalType;       ///< emitted when the mouse rolls over a technology
    typedef boost::signal<void (const Tech*)>      TechDoubleClickedSignalType; ///< emitted when a technology is double-clicked
    //@}

    /** \name Slot Types */ //@{
    typedef TechBrowsedSignalType::slot_type       TechBrowsedSlotType;       ///< type of functor(s) invoked on a TechBrowsedSignalType
    typedef TechClickedSignalType::slot_type       TechClickedSlotType;       ///< type of functor(s) invoked on a TechClickedSignalType
    typedef TechDoubleClickedSignalType::slot_type TechDoubleClickedSlotType; ///< type of functor(s) invoked on a TechDoubleClickedSignalType
    //@}

    /** \name Structors */ //@{
    TechTreeWnd(int w, int h);
    //@}

    /** \name Accessors */ //@{
    const std::string& CategoryShown() const;
    TechTypesShown     GetTechTypesShown() const;

    TechBrowsedSignalType&       TechBrowsedSignal() const       {return m_tech_browsed_sig;}
    TechClickedSignalType&       TechClickedSignal() const       {return m_tech_clicked_sig;}
    TechDoubleClickedSignalType& TechDoubleClickedSignal() const {return m_tech_double_clicked_sig;}
    //@}

    //! \name Mutators //@{
    void ShowCategory(const std::string& category);
    void SetTechTypesShown(TechTypesShown tech_types);
    void UncollapseAll();
    //@}

private:
    class LayoutPanel;

    void TechBrowsedSlot(const Tech* t);
    void TechClickedSlot(const Tech* t);
    void TechDoubleClickedSlot(const Tech* t);
    void TechTypesShownSlot(int types);

    std::vector<CUIButton*> m_category_buttons;
    LayoutPanel*            m_layout_panel;
    GG::RadioButtonGroup*   m_tech_type_buttons;
    CUIButton*              m_uncollapse_all_button;

    mutable TechBrowsedSignalType       m_tech_browsed_sig;
    mutable TechClickedSignalType       m_tech_clicked_sig;
    mutable TechDoubleClickedSignalType m_tech_double_clicked_sig;
};

class TechWnd : public CUI_Wnd
{
public:
    /** \name Structors */ //@{
    TechWnd();
    //@}

private:
    
};

#endif // _TechWnd_h_
