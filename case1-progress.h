/***************************************************************************
 *   Copyright (C) 2003-2007 by Joachim Eibl                               *
 *   joachim.eibl at gmx.de                                                *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 ***************************************************************************/

#ifndef PROGRESS_H
#define PROGRESS_H

#include <QDialog>
#include <QTime>
#include <QList>


class ProgressDialog : public QDialog
{
   Q_OBJECT
public:
   ProgressDialog( QWidget* pParent,QStatusBar* );

   void setStayHidden( bool bStayHidden );
   void setInformation( const QString& info, bool bRedrawUpdate=true );
   void setInformation( const QString& info, int current, bool bRedrawUpdate=true );
   void setCurrent( int current, bool bRedrawUpdate=true  );
   void step( bool bRedrawUpdate=true );
   void setMaxNofSteps( int dMaxNofSteps );
   void addNofSteps( int nofSteps );
   void push();
   void pop(bool bRedrawUpdate=true);


   if (m_pStatusBar)
   {
      m_pStatusBarWidget = new QWidget;
      QHBoxLayout* pStatusBarLayout = new QHBoxLayout(m_pStatusBarWidget);
      pStatusBarLayout->setMargin(0);
      pStatusBarLayout->setSpacing(3);
      m_pStatusProgressBar = new QProgressBar;
      m_pStatusProgressBar->setRange(0, 1000);
      m_pStatusProgressBar->setTextVisible(false);
      m_pStatusAbortButton = new QPushButton( i18n("&Cancel") );
      connect(m_pStatusAbortButton, SIGNAL(clicked()), this, SLOT(slotAbort()));
      pStatusBarLayout->addWidget(m_pStatusProgressBar);
      pStatusBarLayout->addWidget(m_pStatusAbortButton);
      m_pStatusBar->addPermanentWidget(m_pStatusBarWidget,0);
      m_pStatusBarWidget->setFixedHeight(m_pStatusBar->height());
      m_pStatusBarWidget->hide();
   }
   else
   {
      m_pStatusProgressBar = 0;
      m_pStatusAbortButton = 0;
   }


   // The progressbar goes from 0 to 1 usually.
   // By supplying a subrange transformation the subCurrent-values
   // 0 to 1 will be transformed to dMin to dMax instead.
   // Requirement: 0 < dMin < dMax < 1
   void setRangeTransformation( double dMin, double dMax );
   void setSubRangeTransformation( double dMin, double dMax );

   void exitEventLoop();
   void enterEventLoop( KJob* pJob, const QString& jobInfo );

   bool wasCancelled();
   enum e_CancelReason{eUserAbort,eResize};
   void cancel(e_CancelReason);
   e_CancelReason cancelReason();
   void clearCancelState();
   void show();
   void hide();
   void hideStatusBarWidget();
   void delayedHideStatusBarWidget();
   
   virtual void timerEvent(QTimerEvent*);
public slots:
   void recalc(bool bRedrawUpdate);
private:

   struct ProgressLevelData;



// When using the ProgressProxy you need not take care of the push and pop, except when explicit.
class ProgressProxy: public QObject
{
   Q_OBJECT
public:
   ProgressProxy();
   ~ProgressProxy();
   
   void setInformation( const QString& info, bool bRedrawUpdate=true );
   void setInformation( const QString& info, int current, bool bRedrawUpdate=true );
   void setCurrent( int current, bool bRedrawUpdate=true  );
   void step( bool bRedrawUpdate=true );
   void setMaxNofSteps( int maxNofSteps );
   void addNofSteps( int nofSteps );
   bool wasCancelled();
   void setRangeTransformation( double dMin, double dMax );
   void setSubRangeTransformation( double dMin, double dMax );

   static void exitEventLoop();
   static void enterEventLoop( KJob* pJob, const QString& jobInfo );
   static QDialog *getDialog();
   static void recalc();
private:
};

extern ProgressDialog* g_pProgressDialog;

#endif



   m_pInformation = new QLabel( " ", this );
   layout->addWidget( m_pInformation );

   m_pProgressBar = new QProgressBar();
   m_pProgressBar->setRange(0,1000);
   layout->addWidget( m_pProgressBar );

   m_pSubInformation = new QLabel( " ", this);
   layout->addWidget( m_pSubInformation );

   m_pSubProgressBar = new QProgressBar();
   m_pSubProgressBar->setRange(0,1000);
   layout->addWidget( m_pSubProgressBar );

